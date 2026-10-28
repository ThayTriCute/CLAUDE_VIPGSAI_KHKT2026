"""Shared instructions for data the existing web renderer can display."""

WEB_QUESTION_INSTRUCTION = r'''
HỢP ĐỒNG CÂU HỎI TRÊN WEB:
- q/opt/stmts chỉ chứa văn bản, công thức KaTeX trong $...$ hoặc $$...$$; không chèn tài liệu LaTeX, center, tikzpicture, tkzTab hoặc mã vẽ vào các chuỗi này.
- Câu đọc đồ thị phải kèm dữ liệu hình trong cùng object: ví dụ f={"type":"func_3","a":1,"b":0,"c":-3,"d":1}, đồng thời nêu rõ hàm số số học tương ứng. Các hệ số phải là số; không dùng chữ tham số thay hệ số của hình.
- Bảng biến thiên dùng trường bbt là chuỗi nhiều dòng phân cách bằng |, ví dụ: "x | -inf | -1 | 1 | +inf\ny' | + | 0 | - | 0 | +\ny | -inf | 3 | -1 | +inf". Không dùng mã TikZ làm hình web. Bảng số liệu dùng mslgn_data với groups và freq cùng độ dài.
- Mỗi câu trắc nghiệm có đúng một phương án đúng. Tự xét cả bốn phương án độc lập: một khoảng con của khoảng đồng biến/nghịch biến cũng là phương án đúng, không chỉ khoảng tối đại. Không đặt hai khoảng cùng thỏa mãn.
- Thiếu dữ liệu hình thì biên soạn lại toàn câu và các phương án/khóa chấm đồng bộ, giữ đúng môn/lớp/chủ đề/mức độ; không đoán hình gốc hoặc chỉ sửa một đáp án.
'''


def replacement_schema(part, subject, grade, topics, level=''):
    question = {'subject': subject, 'grade': grade, 'topic': topics[0] if topics else '',
                'q': 'Nội dung đầy đủ của một câu thay thế', 'level': level,
                'explain': 'Lập luận nội bộ để kiểm tra khóa chấm',
                'socratic_hint': 'Một câu hỏi gợi mở theo ngữ cảnh, không nêu lời giải hoặc đáp án'}
    if part == 'p1':
        question.update(opt=['A. ...', 'B. ...', 'C. ...', 'D. ...'], ans='A')
    elif part == 'p2':
        question['stmts'] = [{'t': f'Mệnh đề {i}', 'a': True} for i in range(1, 5)]
    else:
        question['ans'] = 'Đáp số cùng đơn vị/quy tắc làm tròn phù hợp'
    return {'replacement_question': question}
