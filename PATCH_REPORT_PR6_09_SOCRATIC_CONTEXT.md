# Bản vá 09: gợi mở dự phòng bám mục tiêu câu hỏi

## Hai ca Cloud đã quan sát

Đề7798, Trạm3 Toán12: câu hỏi tọa độ cực tiểu nhận anchor đếm số điểm cực trị; câu hỏi tung độ giao trục tung nhận hướng dẫn chung nhiều bước không nhắc trục tung. Người dùng cũng gửi ảnh của trường hợp thứ hai.

## Nguyên nhân

Hàm sanitize_socratic_hint đã ưu tiên gợi mở riêng nếu qua guiding_question. Khi gợi mở thiếu hoặc không qua kiểm hình thức, các anchor từ khóa và fallback chung được dùng. Kho đó chưa phân biệt hai mục tiêu cụ thể trên. Tiêu đề wrapper của giao diện và tiêu đề trong anchor cũng có thể trông như hai luồng; hàm này không gọi API. Benchmark riêng local1000lần27.108ms, không phải phép đo độ trễ Cloud.

## Thay đổi và bảo toàn

Thêm fallback dạng câu hỏi cho giao trục tung và tọa độ điểm cực đại/cực tiểu, sau bước ưu tiên gợi mở riêng hợp lệ và trước anchor chung. Không tính số, nêu nghiệm hay phương án. Nội dung mới là câu hỏi thuần, không chèn thêm tiêu đề định hướng bên trong khối. Không thay layout, radio, đáp án, giải thích, Polya hoặc các công cụ. Môn khác và các loại câu chưa nhận diện giữ luồng cũ; không tăng API/retry.

## Kiểm và giới hạn

Bảy kiểm thử riêng: hai ca thật, cực đại/cực tiểu đúng mục tiêu, giữ gợi mở hợp lệ, từ chối chỉ định đáp án rõ ràng, giữ fallback cho câu khác, giữ đường môn/lớp65ngữcảnh. Đây là kiểm hợp đồng bằng fixture; chưa phải nghiệm thu Cloud65cặp hay kiểm chứng mọi gợi mở tự do.

Không khẳng định guiding_question có thể phát hiện mọi gợi ý lộ đáp án hoặc lệch ngữ cảnh bằng diễn đạt gián tiếp. Các loại câu khác cần được rà tiếp theo checklist; không ghi toàn bộ Socratic đã hoàn chỉnh từ bản vá này.

Chốt hồi quy local: 227/227 đạt trong 170.101 giây; bảy ca riêng đạt. Thời gian chạy bộ test không phải độ trễ của app. Chưa ghi nghiệm thu Cloud trước triển khai.
