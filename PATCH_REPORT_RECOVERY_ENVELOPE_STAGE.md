# Tách lỗi cú pháp JSON khỏi lỗi vỏ phản hồi phục dựng

ReproCloud94a22e5: đềToán12/KSHS12–4–6sau120.254scậntrênkhôngmở; p1câu1và9 missing_source_visual, hai phản hồi thay thế decodeValueError, p2câu1thiếuhìnhhếttrần2calls. Không gọi lại đề để đoán.

Nguyên nhân chẩn đoán thiếu độ phân giải: stage decode bao gồm cả safe_json_loads và kiểm root replacement_question. ValueError có thể là JSON sai cú pháp hoặc JSON đúng nhưng sai wrapper; log hiện tại không phân biệt.

Sửa quan sát: đặt stage envelope sau khi parse thành công và cho phép mã cố định này trong log. Không đổi parser, quyền xuất đề, câu/phương án/key, UI hoặc budget/retry. Không ghi rawresponse,prompt,key,tênHS hay exceptiontext. Lỗi gốc chưa được sửa bởi thay đổi chẩn đoán này.

LocalkhôngAPI32/32qua4.277s, gồm saiwrapper dạngJSONđúng,privacy, không tăngcall, giữsource,58ngữcảnhnonliterature và7Ngữvăn, JSONsyntax/LaTeX/duplicate/truncation. Diffcheckqua. CI phải qua trướcmerge. Không chạy lặp toànAppTest vì không đổiUI.

Giá trị: lần lỗi sau biết phải sửa decoder hay hợp đồng output thay vì gọiAI lại mù. Giới hạn: chưa biết nguyên nhân của hai phản hồi Cloud cũ, không thể phân loại hồi tố từ log đã mấtchi tiết.
