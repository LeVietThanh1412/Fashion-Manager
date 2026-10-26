// Cấu hình các bảng và form. Tên trường trùng tên cột MySQL để dễ đọc.
const roles = {admin:'Chủ thương hiệu',regional_manager:'Quản lý khu vực',store_manager:'Quản lý cửa hàng',staff:'Nhân viên'};
const regions = {1:'Miền Bắc',2:'Miền Trung',3:'Miền Nam'};
const ranks = {staff:1,store_manager:2,regional_manager:3,admin:4};
const levels = {1:'Thử việc',2:'Chính thức',3:'Trưởng ca'};
const resources = {
  products: {api:'products',title:'Sản phẩm',pk:'ma_san_pham',hint:'Mỗi mã là một biến thể màu sắc và kích cỡ. Giá hiện hành dùng một cột gia_san_pham.',
    columns:[['ma_san_pham','Mã'],['ten_san_pham','Tên sản phẩm'],['ten_danh_muc','Danh mục'],['mau_sac','Màu sắc'],['kich_co','Kích cỡ'],['gia_san_pham','Giá',formatVND]],
    fields:[['ma_san_pham','Mã sản phẩm'],['ma_danh_muc','Danh mục','categories'],['ten_san_pham','Tên sản phẩm'],['mau_sac','Màu sắc'],['kich_co','Kích cỡ'],['gia_san_pham','Giá sản phẩm','number']]},
  categories: {api:'categories',title:'Danh mục',pk:'ma_danh_muc',hint:'Nhóm sản phẩm trong toàn chuỗi.',columns:[['ma_danh_muc','Mã'],['ten_danh_muc','Tên danh mục'],['so_san_pham','Số sản phẩm']],fields:[['ma_danh_muc','Mã danh mục'],['ten_danh_muc','Tên danh mục']]},
  settings: {api:'stores',title:'Cửa hàng',pk:'ma_cua_hang',hint:'Danh sách cửa hàng trong phạm vi được phân công.',columns:[['ma_cua_hang','Mã'],['ten_cua_hang','Tên cửa hàng'],['khu_vuc','Khu vực',v=>regions[v]],['dia_chi','Địa chỉ'],['so_dien_thoai','Điện thoại'],['email','Email']],
    fields:[['ma_cua_hang','Mã cửa hàng'],['ten_cua_hang','Tên cửa hàng'],['khu_vuc','Khu vực','region'],['dia_chi','Địa chỉ'],['so_dien_thoai','Điện thoại'],['email','Email','email']]},
  employees: {api:'employees',title:'Nhân sự & phân quyền',pk:'ma_nhan_vien',hint:'Cấp trên quản lý cấp dưới trong phạm vi được giao. Cấp bậc nhân viên: thử việc → chính thức → trưởng ca; có thể hạ bậc và chỉnh lương.',
    columns:[['ma_nhan_vien','Mã'],['ho_ten','Họ tên'],['quyen_han','Vai trò',v=>roles[v]],['ma_cua_hang','Cửa hàng'],['khu_vuc_quan_ly','Khu vực',v=>regions[v]||'—'],['luong','Lương',formatVND],['cap_bac','Cấp bậc',v=>levels[v]],['trang_thai','Trạng thái',v=>v==='active'?'Đang làm việc':'Ngừng làm việc']],
    fields:[['ma_nhan_vien','Mã nhân viên'],['ho_ten','Họ tên'],['so_dien_thoai','Điện thoại'],['email','Email','email'],['quyen_han','Vai trò','role'],['ma_cua_hang','Cửa hàng','stores'],['khu_vuc_quan_ly','Khu vực phụ trách','region'],['ma_quan_ly','Người quản lý trực tiếp','managers'],['luong','Lương (VNĐ)','number'],['cap_bac','Cấp bậc nhân viên','level'],['trang_thai','Trạng thái','status']]},
  customers: {api:'customers',title:'Khách hàng',pk:'ma_khach_hang',hint:'Lưu thông tin khách trước khi lập đơn. Lịch sử mua hàng hiển thị theo phạm vi của người đang xem.',columns:[['ma_khach_hang','Mã'],['ho_ten','Họ tên'],['so_dien_thoai','Điện thoại']],fields:[['ma_khach_hang','Mã khách hàng'],['ho_ten','Họ tên'],['so_dien_thoai','Điện thoại']]},
  orders: {api:'orders',title:'Đơn hàng',pk:'ma_don_hang',hint:'Chọn khách hàng, nhân viên lập và ít nhất một sản phẩm. Giá đã lưu được giữ nguyên khi giá danh mục thay đổi.',
    columns:[['ma_don_hang','Mã đơn'],['ngay_tao_don','Ngày lập',dateTime],['ma_khach_hang','Khách hàng'],['ten_nhan_vien','Người lập'],['ten_cua_hang','Cửa hàng'],['tong_so_luong','Số lượng'],['tong_tien','Tổng tiền',formatVND]],
    fields:[['ma_don_hang','Mã đơn hàng'],['ma_nhan_vien','Nhân viên lập','receivers'],['ma_khach_hang','Khách hàng','customers'],['ngay_tao_don','Ngày tạo đơn','datetime-local']]},
  distributions: {api:'distributions',title:'Phân phối',pk:'ma_phan_phoi',hint:'Nhân viên được xem số lượng từng sản phẩm phân phối về cửa hàng. Nhân viên nhận phải thuộc cửa hàng nhận.',
    columns:[['ma_phan_phoi','Mã phiếu'],['ngay_phan_phoi','Ngày phân phối',dateTime],['ten_cua_hang','Cửa hàng nhận'],['ten_nhan_vien','Người nhận'],['tong_so_luong','Số lượng phân phối']],
    fields:[['ma_phan_phoi','Mã phiếu'],['ma_cua_hang','Cửa hàng nhận','stores'],['ma_nhan_vien','Nhân viên nhận','receivers'],['ngay_phan_phoi','Ngày phân phối','date']]},
};
const resourceState = {};
let activeTab = 'analytics';
let editor = null;
let lookups = {};
let resourceRequest = 0;

function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function dateTime(value) {
  if (!value) return '—';
  // MySQL DATETIME là giờ Việt Nam; không chuyển thành UTC lần nữa.
  const [day,clock] = String(value).split('T');
  const parts = day.split('-');
  return parts.length===3 ? `${parts[2]}/${parts[1]}/${parts[0]}${clock?' '+clock.slice(0,5):''}` : value;
}
function localNow() {
  const parts = new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Ho_Chi_Minh',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(new Date());
  return parts.replace(' ','T');
}
function isDocument(resource) { return ['orders','distributions'].includes(resource); }
function canWrite(resource,row) {
  if (!actor) return false;
  if (resource==='employees') return actor.quyen_han!=='staff' && (!row || ranks[row.quyen_han]<ranks[actor.quyen_han]);
  if (['products','categories','settings'].includes(resource)) return actor.quyen_han==='admin';
  if (resource==='distributions') return ['admin','regional_manager'].includes(actor.quyen_han);
  return true;
}
function canDelete(resource,row) {
  return canWrite(resource,row) && (resource!=='customers' || actor.quyen_han==='admin');
}
function applyRole() {
  document.getElementById('actorName').textContent = actor.ho_ten;
  const scope = actor.quyen_han==='admin'?'Toàn chuỗi':actor.quyen_han==='regional_manager'?regions[actor.khu_vuc_quan_ly]:actor.ma_cua_hang;
  document.getElementById('actorScope').textContent = `${roles[actor.quyen_han]} · ${scope}`;
  document.getElementById('scopeBadge').textContent = `${roles[actor.quyen_han]} · ${scope}`;
  const allowed = ['analytics','products','categories','settings','customers','distributions','orders'];
  if (actor.quyen_han!=='staff') allowed.push('employees','reports');
  if (actor.quyen_han==='admin') allowed.push('queries');
  document.querySelectorAll('.nav-btn').forEach(btn=>btn.classList.toggle('hidden',!allowed.includes(btn.dataset.tab)));
  if (!allowed.includes(activeTab)) activeTab='analytics';
  Object.keys(resources).forEach(key=>{
    document.getElementById(key+'Add').classList.toggle('hidden',!canWrite(key));
    document.getElementById(key+'Hint').textContent = resources[key].hint;
  });
  updateTabVisibility();
}
function updateTabVisibility() {
  document.querySelectorAll('[id^="tab-"]').forEach(el=>el.classList.toggle('hidden',el.id!=='tab-'+activeTab));
  document.querySelectorAll('.nav-btn').forEach(btn=>btn.classList.toggle('active',btn.dataset.tab===activeTab));
  document.getElementById('pageTitle').textContent = resources[activeTab]?.title || ({analytics:'Trang chủ',reports:'Báo cáo doanh thu',queries:'Truy vấn BTL'})[activeTab];
}
async function switchTab(tab) {
  const button = document.querySelector(`.nav-btn[data-tab="${tab}"]`);
  if (!actor || !button || button.classList.contains('hidden')) return;
  activeTab=tab;
  updateTabVisibility();
  if (window.innerWidth<768) {
    document.getElementById('sidebar').classList.add('-translate-x-full');
    document.getElementById('mobileBackdrop').classList.add('hidden');
  }
  return loadActiveTab();
}
function loadActiveTab() {
  document.getElementById('pageError').textContent='';
  if (activeTab==='analytics') return loadSalesAnalytics();
  if (activeTab==='reports') return loadReports();
  if (activeTab==='queries') return loadQueries();
  return loadResource(activeTab);
}

function tableHTML(columns,items,actions) {
  if (!items.length) return '<p class="empty-state">Không có dữ liệu phù hợp.</p>';
  return `<table class="data-table"><thead><tr>${columns.map(c=>`<th>${escapeHTML(c[1])}</th>`).join('')}${actions?'<th>Thao tác</th>':''}</tr></thead><tbody>${items.map((row,index)=>`<tr>${columns.map(c=>`<td>${escapeHTML(c[2]?c[2](row[c[0]]):row[c[0]]??'—')}</td>`).join('')}${actions?`<td><div class="row-actions">${actions(row,index)}</div></td>`:''}</tr>`).join('')}</tbody></table>`;
}
async function loadResource(resource) {
  const state = resourceState[resource] ||= {page:0,items:[],total:0};
  const container = document.getElementById(resource+'Body');
  const generation = ++resourceRequest;
  container.innerHTML='<p class="empty-state">Đang tải dữ liệu...</p>';
  document.getElementById(resource+'Pager').innerHTML='';
  try {
    const search=document.getElementById(resource+'Search').value;
    const data=await apiRequest(`/api/${resources[resource].api}?limit=20&offset=${state.page*20}&search=${encodeURIComponent(search)}`);
    if (generation!==resourceRequest) return true;
    if (state.page>0 && !data.items.length) { state.page--; return loadResource(resource); }
    state.items=data.items; state.total=data.total;
    const action=(label,action,index)=>`<button type="button" class="btn small" data-action="${action}" data-index="${index}">${label}</button>`;
    container.innerHTML=tableHTML(resources[resource].columns,data.items,(row,index)=>[
      isDocument(resource)?action('Chi tiết','view',index):'',
      canWrite(resource,row)?action(resource==='employees'?'Lương / phân quyền':'Sửa','edit',index):'',
      resource==='customers'?action('Lịch sử mua','history',index):'',
      canDelete(resource,row)?action('Xóa','delete',index):''
    ].join(''));
    container.querySelectorAll('[data-action]').forEach(button=>button.addEventListener('click',()=>{
      const row=state.items[Number(button.dataset.index)];
      const id=row[resources[resource].pk];
      if (button.dataset.action==='delete') return deleteRecord(resource,id);
      if (button.dataset.action==='history') return showCustomerHistory(id);
      return openEditor(resource,id,button.dataset.action==='view');
    }));
    const pager=document.getElementById(resource+'Pager');
    pager.innerHTML=`<span>${data.total} bản ghi · Trang ${state.page+1}/${Math.max(1,Math.ceil(data.total/20))}</span><button type="button" class="btn small" id="pagePrev" ${state.page===0?'disabled':''}>Trước</button><button type="button" class="btn small" id="pageNext" ${(state.page+1)*20>=data.total?'disabled':''}>Sau</button>${resource==='employees'?'<button type="button" class="btn small" id="staffHistory">Lịch sử bổ nhiệm</button>':''}`;
    pager.querySelector('#pagePrev').onclick=()=>{state.page--;loadResource(resource);};
    pager.querySelector('#pageNext').onclick=()=>{state.page++;loadResource(resource);};
    if (resource==='employees') pager.querySelector('#staffHistory').onclick=showAssignmentHistory;
    return true;
  } catch(error) { container.innerHTML=`<p class="form-error">${escapeHTML(error.message)}</p>`; return false; }
}
function searchResource(resource) {
  (resourceState[resource] ||= {}).page=0;
  return loadResource(resource);
}
async function allRows(resource) {
  const items=[];
  let total;
  do {
    const data=await apiRequest(`/api/${resource}?limit=500&offset=${items.length}`);
    items.push(...data.items); total=data.total;
    if (!data.items.length) break;
  } while (items.length<total);
  return items;
}
function optionHTML(value,label,selected) {
  return `<option value="${escapeHTML(value)}" ${String(value)===String(selected)?'selected':''}>${escapeHTML(label)}</option>`;
}
function lookupOptions(type,value) {
  if (type==='region') return '<option value="">— Chọn khu vực —</option>'+Object.entries(regions).map(([k,v])=>optionHTML(k,v,value)).join('');
  if (type==='role') return Object.entries(roles).filter(([role])=>ranks[role]<ranks[actor.quyen_han]).map(([k,v])=>optionHTML(k,v,value)).join('');
  if (type==='level') return Object.entries(levels).map(([k,v])=>optionHTML(k,v,value)).join('');
  if (type==='status') return optionHTML('active','Đang làm việc',value)+optionHTML('inactive','Ngừng làm việc',value);
  const map={categories:['ma_danh_muc','ten_danh_muc'],stores:['ma_cua_hang','ten_cua_hang'],customers:['ma_khach_hang','ho_ten'],managers:['ma_nhan_vien','ho_ten'],receivers:['ma_nhan_vien','ho_ten']};
  const [pk,label]=map[type];
  return `<option value="">${type==='managers'?'— Chưa phân công —':'— Chọn —'}</option>`+(lookups[type]||[]).map(row=>optionHTML(row[pk],`${row[pk]} · ${row[label]}`,value)).join('');
}
async function openEditor(resource,id=null,readOnly=false) {
  try {
    const config=resources[resource];
    let row=id?resourceState[resource]?.items.find(item=>item[config.pk]===id):null;
    if (id && isDocument(resource)) row=await apiRequest(`/api/${config.api}/${encodeURIComponent(id)}`);
    editor={resource,id,readOnly,row:row||{}};
    lookups={};
    const needed=new Set(config.fields.map(f=>f[2]).filter(type=>['categories','stores','customers','receivers','managers'].includes(type)));
    const tasks=[...needed].map(async type=>{
      if (type==='receivers'||type==='managers') {
        lookups[type]=actor.quyen_han==='staff'?[actor]:(await allRows('employees')).filter(row=>row.trang_thai==='active');
      } else lookups[type]=await allRows(type);
    });
    if (isDocument(resource)) tasks.push(allRows('products').then(items=>lookups.products=items));
    await Promise.all(tasks);
    if (row && lookups.receivers && !lookups.receivers.some(n=>n.ma_nhan_vien===row.ma_nhan_vien)) {
      lookups.receivers.push({ma_nhan_vien:row.ma_nhan_vien,ho_ten:row.ten_nhan_vien,ma_cua_hang:row.cua_hang_giao_dich});
    }
    const defaults={quyen_han:'staff',ma_cua_hang:actor.ma_cua_hang||'',khu_vuc_quan_ly:'',ma_quan_ly:actor.quyen_han!=='staff'?actor.ma_nhan_vien:'',luong:0,cap_bac:2,trang_thai:'active',ngay_tao_don:localNow(),ngay_phan_phoi:localNow().slice(0,10),ma_nhan_vien:actor.ma_cua_hang?actor.ma_nhan_vien:''};
    document.getElementById('editorTitle').textContent=`${readOnly?'Chi tiết':id?'Cập nhật':'Thêm'} · ${config.title}`;
    document.getElementById('editorError').textContent='';
    document.getElementById('editorSave').classList.toggle('hidden',readOnly);
    document.getElementById('editorFields').innerHTML=config.fields.map(([key,label,type='text'])=>{
      let value=row?.[key]??(resource==='employees'&&key==='ma_nhan_vien'?'':defaults[key])??'';
      if (type==='datetime-local') value=String(value).slice(0,16);
      const disabled=readOnly || (id && (key===config.pk || (isDocument(resource)&&key==='ma_nhan_vien') || (resource==='distributions'&&key==='ma_cua_hang')));
      const optional=['ma_cua_hang','khu_vuc_quan_ly','ma_quan_ly'].includes(key)&&resource==='employees';
      const options=['categories','stores','customers','receivers','managers','region','role','level','status'];
      const control=options.includes(type)?`<select name="${key}" ${disabled?'disabled':''} ${optional?'':'required'}>${lookupOptions(type,value)}</select>`:
        `<input name="${key}" type="${type}" value="${escapeHTML(value)}" ${disabled?'disabled':''} ${optional?'':'required'} ${type==='number'?`min="0" step="${key==='luong'?'0.01':'1'}"`:''} ${type==='text'?`maxlength="${key==='mau_sac'?50:key.startsWith('ma_')||key==='kich_co'?20:key==='so_dien_thoai'?25:255}"`:''}>`;
      return `<label data-field="${key}">${label}${control}</label>`;
    }).join('');
    document.getElementById('editorExtra').innerHTML='';
    if (resource==='employees') {
      employeeFieldsChanged();
      ['quyen_han','ma_cua_hang','khu_vuc_quan_ly'].forEach(key=>document.getElementById('editorForm').elements[key].addEventListener('change',employeeFieldsChanged));
      document.getElementById('editorExtra').innerHTML='<p class="muted mt-4">Bổ nhiệm vào vị trí đang có người: quản lý cửa hàng cũ trở thành nhân viên; quản lý khu vực cũ ngừng giữ quyền. Cấp dưới được chuyển sang người mới. Lịch sử bổ nhiệm được lưu lại.</p>';
    }
    if (isDocument(resource)) {
      document.getElementById('editorExtra').innerHTML=`<div class="line-toolbar"><strong>Danh sách sản phẩm</strong>${readOnly?'':'<button type="button" class="btn small" id="addLine">+ Thêm sản phẩm</button>'}</div><div class="table-wrap"><table class="data-table line-table"><thead><tr><th>Sản phẩm · màu · cỡ</th><th>Số lượng</th>${resource==='orders'?'<th>Đơn giá</th><th>Thành tiền</th>':''}<th></th></tr></thead><tbody id="documentLines"></tbody></table></div><div class="line-total" id="documentTotal"></div>`;
      for (const line of row?.chi_tiet||[{}]) addDocumentLine(line);
      if (!readOnly) document.getElementById('addLine').onclick=()=>addDocumentLine();
      if (resource==='distributions') {
        document.getElementById('editorForm').elements.ma_cua_hang.onchange=filterReceivers;
        filterReceivers();
      }
    }
    const dialog=document.getElementById('editorDialog');
    if (!dialog.open) dialog.showModal();
  } catch(error) { showToast(error.message); }
}

function employeeFieldsChanged(event) {
  const form=document.getElementById('editorForm');
  const role=form.elements.quyen_han.value;
  const regional=role==='regional_manager';
  const store=form.elements.ma_cua_hang;
  const region=form.elements.khu_vuc_quan_ly;
  store.disabled=regional; store.required=!regional;
  region.disabled=!regional; region.required=regional;
  document.querySelector('[data-field="ma_cua_hang"]').classList.toggle('hidden',regional);
  document.querySelector('[data-field="khu_vuc_quan_ly"]').classList.toggle('hidden',!regional);
  const manager=form.elements.ma_quan_ly;
  const old=event&&['ma_cua_hang','quyen_han'].includes(event.target.name)?'':manager.value;
  const selectedStore=(lookups.stores||[]).find(s=>s.ma_cua_hang===store.value);
  const suitable=(lookups.managers||[]).filter(m=>ranks[m.quyen_han]>ranks[role] && (m.quyen_han==='admin'||(m.quyen_han==='regional_manager'&&m.khu_vuc_quan_ly===selectedStore?.khu_vuc)||(m.quyen_han==='store_manager'&&m.ma_cua_hang===store.value)));
  manager.innerHTML=optionHTML('','— Chưa phân công —',old)+suitable.map(m=>optionHTML(m.ma_nhan_vien,`${m.ma_nhan_vien} · ${m.ho_ten}`,old)).join('');
  if (!manager.value && suitable.length) manager.value=suitable.sort((a,b)=>ranks[a.quyen_han]-ranks[b.quyen_han])[0].ma_nhan_vien;
}
function filterReceivers() {
  const form=document.getElementById('editorForm');
  const receiver=form.elements.ma_nhan_vien;
  const value=receiver.value;
  receiver.innerHTML=optionHTML('','— Chọn nhân viên nhận —',value)+(lookups.receivers||[]).filter(n=>n.ma_cua_hang===form.elements.ma_cua_hang.value).map(n=>optionHTML(n.ma_nhan_vien,`${n.ma_nhan_vien} · ${n.ho_ten}`,value)).join('');
}
function addDocumentLine(line={}) {
  const readOnly=editor.readOnly;
  const isOrder=editor.resource==='orders';
  const row=document.createElement('tr');
  const productOptions=optionHTML('','— Chọn sản phẩm —',line.ma_san_pham)+(lookups.products||[]).map(p=>optionHTML(p.ma_san_pham,`${p.ma_san_pham} · ${p.ten_san_pham} · ${p.mau_sac} · ${p.kich_co}`,line.ma_san_pham)).join('');
  row.innerHTML=`<td><select class="line-product" required ${readOnly?'disabled':''}>${productOptions}</select></td><td><input class="line-quantity" type="number" min="1" max="2147483647" step="1" required value="${escapeHTML(line.so_luong??1)}" ${readOnly?'disabled':''}></td>${isOrder?`<td><input class="line-price" type="number" min="0" step="1" required value="${escapeHTML(line.don_gia_ban??'')}" ${readOnly?'disabled':''}></td><td class="line-amount"></td>`:''}<td>${readOnly?'':'<button type="button" class="btn small danger line-remove">Bỏ</button>'}</td>`;
  document.getElementById('documentLines').appendChild(row);
  row.querySelector('.line-product').addEventListener('change',()=>{
    if (isOrder) row.querySelector('.line-price').value=lookups.products.find(p=>p.ma_san_pham===row.querySelector('.line-product').value)?.gia_san_pham??'';
    recalculateDocument();
  });
  row.querySelectorAll('input').forEach(input=>input.addEventListener('input',recalculateDocument));
  if (!readOnly) row.querySelector('.line-remove').onclick=()=>{row.remove();recalculateDocument();};
  recalculateDocument();
}
function recalculateDocument() {
  let total=0,quantity=0;
  document.querySelectorAll('#documentLines tr').forEach(row=>{
    const count=Number(row.querySelector('.line-quantity').value)||0;
    quantity+=count;
    if (editor.resource==='orders') {
      const amount=count*(Number(row.querySelector('.line-price').value)||0);
      total+=amount;
      row.querySelector('.line-amount').textContent=formatVND(amount);
    }
  });
  document.getElementById('documentTotal').textContent=editor.resource==='orders'?`Tổng tiền: ${formatVND(total)}`:`Tổng số lượng phân phối: ${quantity}`;
}
async function saveEditor(event) {
  event.preventDefault();
  if (!editor || editor.readOnly) return;
  const button=document.getElementById('editorSave');
  const error=document.getElementById('editorError');
  error.textContent=''; button.disabled=true;
  try {
    const config=resources[editor.resource];
    const form=document.getElementById('editorForm');
    const data={};
    for (const [key,,type] of config.fields) {
      const value=form.elements[key].value.trim();
      data[key]=['number','level','region'].includes(type)?(value===''?null:Number(value)):value;
    }
    if (editor.resource==='employees') {
      data.ma_cua_hang=data.quyen_han==='regional_manager'?null:data.ma_cua_hang;
      data.khu_vuc_quan_ly=data.quyen_han==='regional_manager'?data.khu_vuc_quan_ly:null;
      data.ma_quan_ly=data.ma_quan_ly||null;
    }
    if (isDocument(editor.resource)) {
      data.chi_tiet=[...document.querySelectorAll('#documentLines tr')].map(row=>{
        const line={ma_san_pham:row.querySelector('.line-product').value,so_luong:Number(row.querySelector('.line-quantity').value)};
        if (editor.resource==='orders') line.don_gia_ban=Number(row.querySelector('.line-price').value);
        return line;
      });
      if (!data.chi_tiet.length) throw new Error('Phiếu phải có ít nhất một sản phẩm.');
      if (new Set(data.chi_tiet.map(l=>l.ma_san_pham)).size!==data.chi_tiet.length) throw new Error('Sản phẩm bị trùng. Hãy gộp vào một dòng và cập nhật số lượng.');
    }
    const path=`/api/${config.api}${editor.id?'/'+encodeURIComponent(editor.id):''}`;
    await apiRequest(path,{method:editor.id?'PUT':'POST',body:JSON.stringify(data)});
    closeEditor();showToast('Đã lưu thông tin.');
    await Promise.all([loadResource(editor.resource),loadAnalyticsSummary()]);
  } catch(failure) { error.textContent=failure.message; }
  finally { button.disabled=false; }
}
function closeEditor() { document.getElementById('editorDialog').close(); }
async function deleteRecord(resource,id) {
  if (!window.confirm(`Xóa ${id}? Thao tác chỉ thành công khi dữ liệu không bị ràng buộc bởi lịch sử khác.`)) return;
  try {
    await apiRequest(`/api/${resources[resource].api}/${encodeURIComponent(id)}`,{method:'DELETE'});
    showToast('Đã xóa dữ liệu.');await Promise.all([loadResource(resource),loadAnalyticsSummary()]);
  } catch(error) { showToast(error.message); }
}
function showReadOnlyDialog(title,content) {
  editor={readOnly:true};
  document.getElementById('editorTitle').textContent=title;
  document.getElementById('editorFields').innerHTML='';
  document.getElementById('editorError').textContent='';
  document.getElementById('editorExtra').innerHTML=content;
  document.getElementById('editorSave').classList.add('hidden');
  document.getElementById('editorDialog').showModal();
}
async function showCustomerHistory(id) {
  try {
    const items=[];let total;
    do {
      const data=await apiRequest(`/api/customers/${encodeURIComponent(id)}/history?limit=500&offset=${items.length}`);
      items.push(...data.items);total=data.total;
      if (!data.items.length) break;
    } while (items.length<total);
    showReadOnlyDialog('Lịch sử mua hàng · '+id,`<div class="table-wrap">${tableHTML(resources.orders.columns,items)}</div>`);
  } catch(error) {showToast(error.message);}
}
async function showAssignmentHistory() {
  try {
    const data=await apiRequest('/api/employees/history');
    showReadOnlyDialog('Lịch sử bổ nhiệm',`<div class="table-wrap">${tableHTML([['ma_nhan_vien','Mã'],['ho_ten','Nhân viên'],['quyen_han','Vai trò',v=>roles[v]],['ma_cua_hang','Cửa hàng'],['khu_vuc_quan_ly','Khu vực',v=>regions[v]||'—'],['tu_ngay','Từ ngày',dateTime],['den_ngay','Đến ngày',v=>v?dateTime(v):'Hiện tại']],data.items)}</div>`);
  } catch(error) {showToast(error.message);}
}

async function loadReports() {
  const container=document.getElementById('reportsContent');
  if (!document.getElementById('reportFilters')) {
    container.innerHTML=`<h2>Báo cáo doanh thu</h2><p class="muted">Doanh thu tính từ đơn giá lịch sử. Phạm vi dữ liệu theo khu vực/cửa hàng đang phụ trách.</p><form id="reportFilters" class="report-filters"><label>Từ ngày<input type="date" name="start" value="${localNow().slice(0,4)}-01-01" required></label><label>Đến ngày<input type="date" name="end" value="${localNow().slice(0,10)}" required></label><label>Thống kê theo<select name="group"><option value="store">Cửa hàng</option><option value="region">Khu vực</option><option value="employee">Nhân viên</option><option value="day">Ngày</option><option value="month">Tháng</option></select></label><button type="submit" class="btn primary">Xem báo cáo</button></form><div id="reportResult" aria-live="polite"></div>`;
    document.getElementById('reportFilters').onsubmit=event=>{event.preventDefault();loadReports();};
  }
  const result=document.getElementById('reportResult');
  result.innerHTML='<p class="empty-state">Đang tải báo cáo...</p>';
  try {
    const params=new URLSearchParams(new FormData(document.getElementById('reportFilters')));
    const data=await apiRequest('/api/reports?'+params);
    result.innerHTML=`<p class="badge">${data.total_orders} đơn hàng · Doanh thu ${formatVND(data.total_revenue)}</p><div class="report-section"><h3>Doanh thu bán hàng</h3><div class="table-wrap">${tableHTML([['ma','Mã / thời gian'],['ten','Tên / thời gian'],['so_don','Số đơn'],['so_luong','Số sản phẩm'],['doanh_thu','Doanh thu',formatVND]],data.sales)}</div></div><div class="report-section"><h3>Số lượng phân phối theo cửa hàng</h3><div class="table-wrap">${tableHTML([['ma_cua_hang','Mã'],['ten_cua_hang','Cửa hàng'],['so_phieu','Số phiếu'],['so_luong','Số lượng phân phối']],data.distributions)}</div></div><div class="report-section"><h3>20 sản phẩm bán nhiều nhất</h3><div class="table-wrap">${tableHTML([['ma_san_pham','Mã'],['ten_san_pham','Sản phẩm'],['so_luong','Số lượng bán'],['doanh_thu','Doanh thu',formatVND]],data.products)}</div></div>`;
    return true;
  } catch(error) {result.innerHTML=`<p class="form-error">${escapeHTML(error.message)}</p>`;return false;}
}
async function loadQueries() {
  const container=document.getElementById('queriesContent');
  container.innerHTML='<p class="empty-state">Đang tải danh sách truy vấn...</p>';
  try {
    const data=await apiRequest('/api/queries');
    container.innerHTML=`<h2>50 truy vấn SQL · Bài tập lớn</h2><p class="muted">5 nhóm, mỗi nhóm 10 câu từ cơ bản đến nâng cao. Chọn câu để xem SQL và kết quả thật.</p><div class="search-row mt-4"><select id="querySelect">${data.items.map(q=>optionHTML(q.query_id,q.query_id+' · '+q.title,'')).join('')}</select><button type="button" class="btn primary" id="runQuery">Chạy SELECT</button></div><pre id="querySQL" class="sql-preview"></pre><div id="queryResult" class="table-wrap"></div>`;
    const select=document.getElementById('querySelect');
    const update=()=>document.getElementById('querySQL').textContent=data.items.find(q=>q.query_id===select.value).sql;
    select.onchange=()=>{update();document.getElementById('queryResult').innerHTML='';};
    document.getElementById('runQuery').onclick=async()=>{
      const result=document.getElementById('queryResult');
      result.innerHTML='<p class="empty-state">Đang chạy truy vấn...</p>';
      try {
        const response=await apiRequest('/api/queries/'+select.value);
        result.innerHTML=tableHTML(Object.keys(response.items[0]||{}).map(k=>[k,k]),response.items);
      } catch(error) {result.innerHTML=`<p class="form-error">${escapeHTML(error.message)}</p>`;}
    };
    update();return true;
  } catch(error) {container.innerHTML=`<p class="form-error">${escapeHTML(error.message)}</p>`;return false;}
}
