import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

URL='http://127.0.0.1:8011'
results=[]
errors=[]


async def login(browser,code,mobile=False):
    page=await browser.new_page(viewport={'width':390,'height':844} if mobile else {'width':1440,'height':1050})
    page.on('pageerror',lambda error:errors.append(str(error)))
    await page.route('**/config.js',lambda route:route.fulfill(content_type='application/javascript',body=f'window.FASHION_MANAGER_API_URL="{URL}";'))
    await page.goto(URL)
    await page.locator(f'#loginAccount option[value="{code}"]').wait_for(state='attached')
    await page.select_option('#loginAccount',code)
    await page.locator('#loginForm button[type=submit]').click()
    await page.locator('#actorScope').filter(has_text=' · ').wait_for()
    await page.wait_for_function("document.querySelector('#syncBtn').disabled === false && document.querySelector('#summaryProducts').textContent !== '—'")
    return page


async def tab(page,key,mobile=False):
    if mobile:
        await page.locator('#mobileMenuBtn').click()
    await page.locator(f'.nav-btn[data-tab="{key}"]').click()
    if key not in ['analytics','queries','reports']:
        await page.locator(f'#{key}Body tbody tr').first.wait_for()


async def form(page,key,values):
    await page.locator(f'#{key}Add').click()
    await page.locator('#editorDialog[open]').wait_for()
    for field,value in values.items():
        locator=page.locator(f'#editorForm [name="{field}"]')
        if await locator.evaluate('(el)=>el.tagName')=='SELECT':
            await locator.select_option(str(value))
        else:
            await locator.fill(str(value))
    await page.locator('#editorSave').click()
    await page.locator('#editorDialog').wait_for(state='hidden')


async def search(page,key,text):
    await page.locator(f'#{key}Search').fill(text)
    await page.locator(f'#tab-{key} .search-row button').click()
    await page.locator(f'#{key}Body tbody tr').first.wait_for()


async def delete(page,key,text):
    await search(page,key,text)
    page.once('dialog',lambda dialog:dialog.accept())
    await page.locator(f'#{key}Body [data-action="delete"]').first.click()
    await page.locator(f'#{key}Body .empty-state').wait_for()


async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
        admin=await login(browser,'NV000')
        assert await admin.locator('.nav-btn:not(.hidden)').count()==10
        for key in ['products','categories','settings','employees','customers','distributions','orders','reports','queries']:
            await tab(admin,key)
        results.append('Admin: all 10 tabs open')
        await admin.locator('#runQuery').click()
        await admin.locator('#queryResult tbody tr').first.wait_for()
        results.append('Academic query runs from UI')

        await tab(admin,'categories')
        await form(admin,'categories',{'ma_danh_muc':'DM_UI','ten_danh_muc':'Danh mục UI'})
        await search(admin,'categories','DM_UI')
        assert 'Danh mục UI' in await admin.locator('#categoriesBody').inner_text()
        await tab(admin,'products')
        await form(admin,'products',{'ma_san_pham':'SP_UI','ma_danh_muc':'DM_UI','ten_san_pham':'Giày kiểm thử UI','mau_sac':'Đen','kich_co':'40','gia_san_pham':250000})
        results.append('Create category and product through UI')

        await tab(admin,'employees')
        await form(admin,'employees',{'ma_nhan_vien':'NV_UI','ho_ten':'Nhân viên UI','so_dien_thoai':'0999123456','email':'ui@example.com','ma_cua_hang':'CH001','luong':'6500000','cap_bac':'3'})
        await search(admin,'employees','NV_UI')
        assert '6.500.000' in await admin.locator('#employeesBody').inner_text()
        results.append('Create employee with salary and level from UI')
        await admin.screenshot(path='tmp/admin-employees.png',full_page=True)

        north=await login(browser,'NV001')
        assert await north.locator('.nav-btn:not(.hidden)').count()==9
        await tab(north,'employees')
        await search(north,'employees','NV_UI')
        await north.locator('#employeesBody [data-action="edit"]').click()
        await north.locator('#editorDialog[open]').wait_for()
        await north.locator('[name=luong]').fill('6000000')
        await north.locator('[name=cap_bac]').select_option('1')
        await north.locator('#editorSave').click()
        await north.locator('#editorDialog').wait_for(state='hidden')
        await north.locator('#employeesBody tbody tr').first.wait_for()
        assert 'Thử việc' in await north.locator('#employeesBody').inner_text()
        await tab(north,'reports')
        await north.locator('#reportResult .badge').wait_for()
        results.append('Regional manager changes salary/level and views regional report')

        manager=await login(browser,'NV004')
        await tab(manager,'employees')
        await search(manager,'employees','NV_UI')
        await manager.locator('#employeesBody [data-action="edit"]').click()
        await manager.locator('#editorDialog[open]').wait_for()
        assert await manager.locator('[name=quyen_han] option').count()==1
        await manager.locator('[name=luong]').fill('5800000')
        await manager.locator('#editorSave').click()
        await manager.locator('#editorDialog').wait_for(state='hidden')
        results.append('Store manager may assign staff role only and edit own staff salary')

        staff=await login(browser,'NV024')
        assert await staff.locator('.nav-btn:not(.hidden)').count()==7
        await tab(staff,'distributions')
        assert not await staff.locator('#distributionsAdd').is_visible()
        await staff.locator('#distributionsBody [data-action=view]').first.click()
        await staff.locator('#documentLines tr').first.wait_for()
        assert 'Tổng số lượng phân phối' in await staff.locator('#documentTotal').inner_text()
        await staff.locator('#editorDialog .dialog-heading button').click()
        await tab(staff,'customers')
        await form(staff,'customers',{'ma_khach_hang':'KH_UI','ho_ten':'Khách UI','so_dien_thoai':'0999123457'})
        await tab(staff,'orders')
        await staff.locator('#ordersAdd').click()
        await staff.locator('#editorDialog[open]').wait_for()
        await staff.locator('[name=ma_don_hang]').fill('DH_UI')
        await staff.locator('[name=ma_khach_hang]').select_option('KH_UI')
        await staff.locator('.line-product').select_option('SP_UI')
        await staff.locator('.line-quantity').fill('2')
        assert '500.000' in await staff.locator('#documentTotal').inner_text()
        await staff.screenshot(path='tmp/staff-order-form.png',full_page=True)
        await staff.locator('#editorSave').click()
        await staff.locator('#editorDialog').wait_for(state='hidden')
        await search(staff,'orders','DH_UI')
        assert '500.000' in await staff.locator('#ordersBody').inner_text()
        results.append('Staff sees assigned distribution quantities and creates a correctly totaled order')

        mobile=await login(browser,'NV024',True)
        await tab(mobile,'orders',True)
        assert await mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
        await mobile.screenshot(path='tmp/staff-mobile.png',full_page=True)
        results.append('Mobile layout: menu works and no page overflow at 390px')

        await delete(staff,'orders','DH_UI')
        await delete(admin,'employees','NV_UI')
        await tab(admin,'customers')
        await delete(admin,'customers','KH_UI')
        await tab(admin,'products')
        await delete(admin,'products','SP_UI')
        await tab(admin,'categories')
        await delete(admin,'categories','DM_UI')
        results.append('UI test records removed')
        await browser.close()
    assert not errors,errors
    Path('tmp/browser-results.json').write_text(json.dumps({'checks':results,'console_errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'checks':results,'console_errors':errors},ensure_ascii=False))

asyncio.run(main())
