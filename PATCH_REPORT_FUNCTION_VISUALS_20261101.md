# BBT và đồ thị Trạm 1 theo hàm số đã chọn

## Vấn đề và thay đổi

Infographic trước đây dùng bảng Markdown nên không dựng được vạch tiệm cận đúng cho phân thức và chỉ có mô tả chữ thay đồ thị. Bản này dùng cùng mô hình SymPy tính đạo hàm, nghiệm, dấu và giới hạn để dựng BBT và đồ thị SVG trên trang bài học và trong ba kiểu phiếu HTML. Không cần TeX server hoặc thêm lượt AI.

- BBT có mũi tên nối giá trị, phân số chính xác, hai giới hạn một phía và vạch kép tiệm cận.
- Đồ thị tách nhánh, có tiệm cận nét đứt; cực trị và tâm đối xứng có đường gióng đến Ox/Oy; đánh dấu giao Ox/Oy và tọa độ. Nghiệm vô tỉ ghi gần đúng có dấu ≈. Khung nhìn ưu tiên các đặc điểm quan trọng để cực trị không dẹt sát trục.
- Giữ đúng ba dạng không suy biến: bậc ba a≠0; phân thức1/1 c≠0 và ad−bc≠0; phân thức2/1 a≠0,d≠0,ae²−bde+cd²≠0. Hạ bậc hoặc khử nhân tử không được tính là ví dụ đạt của dạng đang xét; đầu vào sai điều kiện hiện thông báo và không vẽ.
- Chỉ lấy hàm nêu rõ trong chủ đề; chủ đề chung chỉ suy ra khi phần lý thuyết có một hàm được xác định nhất quán, ngoài code. Nhiều hàm hoặc ký pháp chưa hỗ trợ thì không chọn ngẫu nhiên. Parser AST giới hạn phép toán/hệ số/bậc; không eval văn bản AI.
- Cache tối đa64 kết quả; SymPy đã là dependency của dự án. Không sửa luồng T2/T3 hoặc thêm dịch vụ ngoài.

## Kiểm chứng

-11test mới đạt: ba nhóm dấu đạo hàm bậc ba×hai dấu hệ số, phân thức1/1 tăng/giảm,2/1 có/không cực trị, đầu vào sai điều kiện, phân số, chọn hàm không mơ hồ, parser, LaTeXfrac, ba kiểu xuất, đường gióng/tâm/giao trục.
- Chrome MCP trên bộ xuất thật:30ca gồm14hợp lệ có đủ2SVG và16ngoài dạng bị từ chối,0lỗiKaTeX. EvidenceT1_SGK_FINAL_CHROME_20261101.json và ma trậnT1_SGK_MANIFEST_20261101.json.
- Đã xem ảnh ba dạng trên Chrome: T1_SGK_CUBIC_GUIDES_20261101.png,T1_SGK_GRAPH11_GUIDES_20261101.png,T1_SGK_GRAPH21_GUIDES_20261101.png. Đây là mẫu kiểm kỹ thuật, không chứng nhận toàn bộ chương trình.
- Bài AI2/1 thật sau sửa trước bổ sung gióng cuối đã kiểm có2SVG ở trang bài học và HTMLtải,0tablecũ/0lỗiKaTeX;T1_FIXED_LIVE21_EXPORT_20261101.html. Bài cubiccuối gửi01:26:35.703UTC đã hoàn tất; Chrome MCP trực tiếp xác nhận cả trang bài học và infographic có BBT/đồ thị cùng hàm x³−3x+1, đã lưu snapshot và ảnh. Không AI pending.
- Full trước bổ sung gióng:368/368,265.982s. Lượt full cuối bị ngắt khi công cụ đổi;logpartialkhôngcoilàpass. Lượt recheck bản cuối369/369đạt274.929s,logT1_FUNCTION_VISUALS_FINAL_RECHECK_20261101.log.

## Giới hạn nghiệm thu

Chưa đối chiếu từng trang/phiên bản SGK và mọi hệ số số học. Phạm vi parser gồm biểu thức số theo x, đa thức bậc3 và phân thức mẫu tuyến tính không suy biến; không nhận hàm lượng giác, tham số chưa gán, nhiều mẫu tuyến tính khác nhau hoặc cửa sổ quá lớn. Không lấy testfixture thay nghiệm thu học thuật65cặp. Phần nội dung AI ngoài hình vẫn cần giáo viên duyệt. CI, merge và Cloud chỉ ghi đạt sau khi có bằng chứng thực tế; kiểm Cloud hiện chờ quyền Chrome.