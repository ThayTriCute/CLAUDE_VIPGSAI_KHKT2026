# Hợp đồng phản hồi một câu thay thế

CloudPR54/ad6ab95 đã phân biệt rõ: hai phản hồi thay thế JSON parse được nhưng không đúng vỏ replacement_question (stageenvelope),ba câu thiếu hình chưa khôi phục. Không biết chính xác rootshape cũ vì log chỉ mã an toàn; không tuyên bố đã quan sát direct/output cụ thể.

Sửa hẹp hợp đồng: prompt bỏ schema khỏi metadata output, đưa schema phản hồi ở cuối và yêu cầu rootreplacement_question,khôngecho task/original/output. Adapter nhận đúngmộtquestionobject ở dạngcanonical, bareobjectcóq+subject+grade+topic, hoặc một outputwrapperkhôngmetadataanh em. Không nhậnarray/multipleroot/p1list,khônglấycâuđầutiên,khôngtựđiềnidentity hoặckey.

Sauadapter vẫn toàn bộvalidation cũ: môn/lớp/topic,scope,mứcđộ,visual,structure,khóachấm,symbolic vàaudit. Không đổiUI,EXPLAIN,radiobutton,parserJSON,budget2calls hoặc trần retry. Câu hỏi/phương án/ans không bị sửa chỉ vì đổivỏ.

Được: giảm khả năng lãng phí phản hồi có đúngmộtcâu nhưng khácvỏ, hợpđồngprompt rõhơn. Đánhđổi: các dạng khác/mơhồ vẫn từchối; không phải bù mọi phản hồi. Hạn2calls vẫn có thể không sửa hết3câuthiếuvisual; lỗi này chưa đóng. Chưa kiểm chứng trọn bộ kiếnthức/KNTT hoặc Cloudtriggerbảnmới.

Targeted28/28qua4.268s, REPLACEMENT_ENVELOPE_TARGETED_20261029.log; Full suite269/269qua215.341s (REPLACEMENT_ENVELOPE_FULL_20261029.log), khôngAPI. Chưapush/CI/Cloudởmốcghi.
