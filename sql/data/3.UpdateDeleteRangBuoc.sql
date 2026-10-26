use quan_ly_chuoi_thoi_trang;

create table IF not exists khu_vuc (
    ma_khu_vuc tinyint primary key,
    ten_khu_vuc VARCHAR(30) not null unique,
    check (ma_khu_vuc IN (1, 2, 3))
);

insert ignore into khu_vuc (ma_khu_vuc, ten_khu_vuc) values
    (1, 'Miền Bắc'),
    (2, 'Miền Trung'),
    (3, 'Miền Nam');

alter table cua_hang
    add foreign key (khu_vuc) references khu_vuc(ma_khu_vuc);

alter table nhan_vien
    add column quyen_han enum(
        'quan_ly',
        'quan_ly_khu_vuc',
        'quan_ly_cua_hang',
        'nhan_vien'
    ) not null default 'nhan_vien',
    add column khu_vuc_quan_ly tinyint null;

update nhan_vien as nv
left join (
    select ma_quan_ly, count(*) as so_cap_duoi
    from nhan_vien
    where ma_quan_ly is not null
    group by ma_quan_ly
) as danh_sach_quan_ly
    on danh_sach_quan_ly.ma_quan_ly = nv.ma_nhan_vien
set nv.quyen_han = CasE
        when nv.ma_nhan_vien = 'NV000' then 'quan_ly'
        when nv.ma_nhan_vien IN ('NV001', 'NV002', 'NV003') then 'quan_ly_khu_vuc'
        when nv.ma_cua_hang is not null
             and danh_sach_quan_ly.so_cap_duoi is not null then 'quan_ly_cua_hang'
        else 'nhan_vien'
    end;

update nhan_vien
set khu_vuc_quan_ly = CasE ma_nhan_vien
    when 'NV001' then 1
    when 'NV002' then 2
    when 'NV003' then 3
end
where quyen_han = 'quan_ly_khu_vuc'
  and ma_nhan_vien IN ('NV001', 'NV002', 'NV003');

alter table nhan_vien
    add foreign key (khu_vuc_quan_ly) references khu_vuc(ma_khu_vuc),
    add check (
            (quyen_han = 'quan_ly'
                and ma_cua_hang is null
                and khu_vuc_quan_ly is null)
            or
            (quyen_han = 'quan_ly_khu_vuc'
                and ma_cua_hang is null
                and khu_vuc_quan_ly is not null)
            or
            (quyen_han IN ('quan_ly_cua_hang', 'nhan_vien')
                and ma_cua_hang is not null
                and khu_vuc_quan_ly is null)
        );
