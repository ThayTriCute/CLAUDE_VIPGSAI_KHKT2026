# Đồng bộ infographic khi Cloud giữ bộ xuất HTML cũ

Sau PR64, Cloud đã pull và Updated, trang bài học có BBT/đồ thị mới nhưng HTML trong iframe và tệp tải vẫn dùng module xuất cũ. Rerun nạp lại app.py nhưng không thay đối tượng hàm đã import; hai lần yêu cầu reboot qua UI trả502, không được coi là reboot thành công.

Thêm bước đồng bộ tại điểm xuất phiếu trong app.py: dùng cùng with_function_visuals đã chạy đúng ở trang chính để cập nhật article khi HTML cũ chưa có hình. Bản HTML đã có hình hoặc thông báo từ chối được giữ nguyên, nên không nhân đôi; các môn khác và nội dung chưa xác định một hàm không bị thay. Bản trắng đen giữ nét đen. Không thay cache toàn hệ thống, không thêm API/AI/retry hoặc phụ thuộc dịch vụ reboot.

Kiểm chứng:
- BEFORE: chạy chính các câu lệnh gán export_html trong AST của app với bộ xuất cũ trả HTML không hình: thất bại0!=1; hai testhelper chưa có báo lỗi. T1_EXPORT_CACHE_BEFORE_20261101.log.
- AFTER:3/3testluồngxuất/cache/idempotence/monochrome/nonmathđạt5.877s;11/11function_visualsđạt1.242s;19/19academic_exportsđạt7.916s. T1_EXPORT_CACHE_AFTER_20261101.log.
- Phát lại đúng HTML đã tải từ Cloud qua helper mới trên local, Chrome có2SVG,0bảngcũ,readytrue/errors0,đồthị3đườnggióng/6điểmđánh dấu. ArtifactT1_CLOUD_EXPORT_SYNC_LOCAL_REPLAY_20261101.html. Không tạo lại bài AI.
- Kếtquảfull369/369274.929sđúngbảnPR64;phầnmáytính/đồthịkhôngđổitrongbảnvá này. CIbảnvámới phảiđạttrướcmerge,Cloudphảikiểmlạitrướckếtluậnđãđónglỗi.