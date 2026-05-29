# Kết luận và hướng phát triển

## Tổng kết những kết quả đã đạt được
Xuyên suốt quá trình nghiên cứu và phát triển, đồ án "Hệ thống hỗ trợ chơi Cờ Tỷ Phú phối hợp AI" đã đi từ việc định hình những ý tưởng phác thảo ban đầu, phân bổ yêu cầu cấu trúc nền, cho tới khi định lượng hoàn thiện thành ba mảnh ghép ứng dụng hoàn chỉnh (AI - Backend - Frontend). Sự giao thoa công nghệ đã tạo nên một tập hợp kết quả thiết thực nhất:
- Thứ nhất: Đã triển khai cực kì thành công các mô hình học sâu suy luận độ tin cậy cực cao, đóng gói dưới cấu trúc máy tính nhúng (Resource-constrained Env). Đây là bằng chứng rằng những mô hình trích xuất đặc trưng hình học (Object Detection/Classification) được thực hiện bởi TFLite hoàn toàn có cơ hội định cư ở môi trường không có GPU nếu được tối ưu hóa luồng gọi tính toán và tiền xử lý ảnh đầu vào.
- Thứ hai: Tạo dệt nên một hệ thống phần mềm Back-end xử lý Event-driven với Python - WebSocket siêu cứng cáp. Các kịch bản logic đặc thù trong game Cờ Tỷ Phú như Giao dịch trực tiếp (Trade Card), Vay mượn (Mortgage) hay Bốc lá bài Cơ Hội (Action Cards) đều được mã hóa một cách hệ thống, có cơ chế rollback (dù có thể phức tạp) mang lại cho bàn cờ truyền thống phong cách thể thao E-Sports chuyên nghiệp.
- Thứ ba: Đưa trải nghiệm tương tác (UX - user experience) lên một góc nhìn rất cao quan thông qua giao diện Front-end React mượt tĩnh. Người dùng không phải từ bỏ cảm giác thú vị của việc cầm hạt xúc xắc thả vật lý, những công việc mệt mỏi về cộng trừ tài sản (Calculation Process) nay đã uỷ thác vào điện toán hoá minh bạch tuyệt đối.

## Những giới hạn còn tồn tại
Ngoài những điểm thành tựu sáng chói biểu hiện qua bài kiểm tra năng lực hệ thống chung, thực tế một số khiếm khuyết khó thể phủ nhận vẫn còn là rào cản mang lại trải nghiệm 100% hoành tráng:
- Sức ép môi trường chiếu sáng ánh sáng vật lý xung quanh (Environmental Lighting Conditions): Mô hình phát hiện điểm xúc xắc khá nhạy cảm trong bối cảnh chói sáng loá, hoặc góc bóng tối lớn trên màng chiếu cam. Những vi điểm đó thỉnh thoảng (dù với tỷ lệ nhỏ) làm AI nhầm lẫn con số dẫn tới sự sai pha đồng bộ cho logic xúc xắc của người tham gia.
- Góc độ ống kính cố định (Fixed perspective view): Thiết kế chỉ cung cấp camera bắt góc tĩnh thẳng xuống để có kết quả chính xác, giảm thiểu khó khăn trong việc che lấp của chính đôi tay người khi thả xúc xắc vào khung ngắm; camera không thể quay góc chéo sâu dưới các vật che mờ.
- Rào cản mở rộng phần cứng (Hardcore Logic Limits): Tương đối khó cho bất kì nhà phát triển mới nào để tùy biến thay đổi thêm quy luật đồ nội bộ trên lõi server của backend, việc thêm bớt bộ rulesets game Cờ Tỷ Phú đòi hỏi hiểu rành kịch bản Class Task của Codebase.

## Hướng phát triển trong tương lai
Sản phẩm dù vượt ra phạm vi bảo vệ nhưng chưa dừng bước ở biên giới ứng dụng và giáo dục hiện tại. Hàng loạt nâng cấp sẽ được ưu tiên trong lộ trình (roadmap) để mang tiềm lực hệ thống lên mức cao nhất, có thể kể ra như:
- Áp dụng các kỹ thuật Tiền xử lý dải sáng Động cao (HDR preprocessing techniques) hoặc lọc Histogram equalization để triệt tiêu ảnh hưởng của vấn đề thay đổi môi trường nguồn sáng phòng.
- Định hướng tự tái huấn luyện (Self-retrain Pipeline): Thu thập ngay trên những sai mốc nhận diện của chính bàn đang chơi, lấy hệ thống Feedback (Ví dụ: Người chơi báo nhầm kết quả) để lưu ảnh log lại, tiếp tục phục vụ tái Training cải thiện Model theo thời gian thực (Continual Learning).
- Bổ sung nhiều luồng cảm biến, kết hợp bộ thư viện theo dõi cả bàn tay (MediaPipe Hand Tracking) phát hiện hành vi bốc thẻ bài thay vì chỉ thao tác xúc xắc.
- Tổng quát hóa quy luật cấu trúc File JSON Rules để Engine Backend biến mình thành một Application Layer cung cấp framework cho rất nhiều mô hình trò chơi cờ bàn tương tự trong cuộc sống giải trí con người.
