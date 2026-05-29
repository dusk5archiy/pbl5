# Giới thiệu

## Đặt vấn đề và lý do chọn đề tài
Trong kỷ nguyên số hóa hiện nay, sự giao thoa giữa thế giới vật lý và không gian ảo đang trở thành một xu hướng tất yếu trong quá trình phát triển công nghệ. Trí tuệ nhân tạo (AI), đặc biệt là phân ngành thị giác máy tính (Computer Vision) và Internet vạn vật (IoT), đã có những bước tiến vượt bậc, cho phép máy tính hiểu và tương tác với môi trường thực tế một cách độc lập, chính xác. Mặc dù các công nghệ này thường được áp dụng trong những ngành công nghiệp quy mô lớn như xe tự lái, giám sát an ninh, hay tự động hóa nhà máy, tiềm năng ứng dụng của chúng trong các lĩnh vực giải trí cộng đồng và giáo dục vẫn còn rất lớn và chưa được khai thác triệt để.

Board game (trò chơi cờ bàn), điển hình là Cờ Tỷ Phú (Monopoly), từ lâu đã trở thành một hình thức giải trí phổ biến mang tính kết nối cao. Tuy nhiên, khi chơi theo phương pháp truyền thống, người chơi thường xuyên phải đối mặt với những vấn đề như quản lý tài sản cồng kềnh, tính toán tiền bạc dễ xảy ra sai sót, cũng như khó khăn trong việc theo dõi toàn bộ trạng thái của ván cờ (như bản đồ, nhà cửa, các thẻ phạt). Việc số hóa các trò chơi này thường dẫn đến các phiên bản game thuần túy trên thiết bị di động, vô tình làm mất đi sự tương tác vật lý trực tiếp - yếu tố cốt lõi tạo nên sự hấp dẫn của board game. 

Xuất phát từ thực tế đó, đề tài nghiên cứu "Hệ thống hỗ trợ chơi Cờ Tỷ Phú bằng tương tác vật lý thông qua nền tảng IoT và Thị giác máy tính" được đề xuất. Hệ thống hướng tới việc kết hợp giữa trải nghiệm đổ xúc xắc vật lý truyền thống và sức mạnh xử lý tự động của công nghệ thông tin. Thay vì phải tự đếm điểm xúc xắc, tự cộng trừ tiền, người chơi chỉ việc tung xúc xắc thật trên bàn; hệ thống sử dụng module camera trên máy tính nhúng Raspberry Pi theo dõi chuyển động, bắt khoảnh khắc xúc xắc dừng và tự động phân tích kết quả nhờ các mô hình học máy. Dữ liệu này sau đó được đồng bộ ngay lập tức lên màn hình điều khiển thông qua hệ thống máy chủ, mang đến một ván cờ tự động hóa nhưng vẫn giữ trọn vẹn giá trị tương tác vật lý.

## Mục tiêu nghiên cứu
Mục tiêu tổng quát của đồ án là thiết kế, triển khai và đánh giá một hệ thống hỗ trợ người chơi trò chơi Cờ Tỷ Phú, ứng dụng công nghệ nhận diện hình ảnh trên thiết bị biên (Edge AI) và kiến trúc ứng dụng web thời gian thực.

Để hiện thực hóa mục tiêu tổng quát, đồ án đặt ra các mục tiêu cụ thể như sau:
- Xây dựng mô hình thị giác máy tính nhẹ, có khả năng phát hiện (detect) chính xác vị trí của các viên xúc xắc và phân loại (classify) số điểm trên mặt xúc xắc với tốc độ xử lý theo thời gian thực.
- Thiết kế thuật toán theo dõi chuyển động (Motion Tracking) nhằm xác định chính xác thời điểm xúc xắc ngừng quay để tiến hành bắt nét (capture) hình ảnh với độ ổn định cao.
- Triển khai toàn bộ khối xử lý hình ảnh lên nền tảng máy tính nhúng hạn chế tài nguyên (Raspberry Pi 4) mà không phụ thuộc vào vi xử lý đồ họa (GPU).
- Xây dựng hệ thống logic máy chủ (Backend) nhằm số hóa hoàn toàn luật chơi Cờ Tỷ Phú, quản lý tài sản, ngân hàng, quỹ đất, thẻ cơ hội và đồng bộ trạng thái giữa các người chơi bằng kết nối WebSocket.
- Phát triển giao diện người dùng (Frontend) tương thích đa nền tảng, cho phép người chơi tham gia ván đấu, xem lại bản đồ trực quan, thực hiện các giao dịch và liên kết liền mạch với hệ thống lõi.

## Đối tượng và phạm vi nghiên cứu
Đối tượng nghiên cứu chính của đề tài bao gồm các thuật toán phát hiện, nhận dạng đối tượng (đặc thù là mặt xúc xắc), tối ưu hóa mô hình học sâu (Deep Learning Optimization) cho thiết bị phần cứng nhỏ lẻ. Cùng với đó là kiến trúc phần mềm hướng sự kiện (Event-driven architecture) trên giao thức WebSocket để xử lý dữ liệu ván cờ.

Phạm vi thực hiện của đồ án được giới hạn ở các yếu tố sau:
- Phần cứng: Sử dụng board mạch Raspberry Pi 4 (RAM 4GB) kết nối với một module camera USB tiêu chuẩn.
- Mô hình nhận diện: Giới hạn tập trung vào việc nghiên cứu và tinh chỉnh các cấu trúc mạng YOLO tối giản cùng với một mô hình trích xuất đặc trưng tùy biến (Score01) để phù hợp chạy trực tiếp trên quá trình suy luận CPU (CPU Inference).
- Trò chơi: Áp dụng tập luật chơi tiêu chuẩn của Cờ Tỷ Phú, quản lý tối đa 4-6 người chơi kết nối vào cùng một phiên mạng LAN.

## Phương pháp nghiên cứu
Đồ án sử dụng sự kết hợp giữa các phương pháp nghiên cứu lý thuyết và thực nghiệm:
- Phương pháp phân tích và tổng hợp lý thuyết: Tìm đọc các tài liệu khoa học, bài báo, giáo trình liên quan đến mạng nơ-ron học sâu (CNN), chuyển đổi mô hình TensorFlow Lite độ trễ thấp, kiến trúc FastAPI và React/Next.js. Từ đó xây dựng nền tảng lý luận vững chắc, thiết kế kiến trúc hệ thống phù hợp.
- Phương pháp thu thập dữ liệu: Tiến hành chụp ảnh, xây dựng tập dữ liệu (dataset) hình ảnh xúc xắc đa góc độ, đa điều kiện ánh sáng. Thực hiện dán nhãn (labeling) thủ công dữ liệu để có ground-truth phục vụ huấn luyện mô hình.
- Phương pháp thực nghiệm và tinh chỉnh (Empirical and Fine-tuning method): Huấn luyện các mô hình trên môi trường máy chủ có GPU mạnh mẻ, sau đó áp dụng kỹ thuật lượng tử hóa (Quantization) để nén mô hình. Đưa các mô hình xuống Raspberry Pi chạy thực nghiệm, đánh giá các chỉ số mAP, thời gian suy luận (inference time), FPS và độ trễ (latency) mạng.

## Cấu trúc của đồ án
Báo cáo đồ án được trình bày trình tự và hệ thống, bao gồm các nội dung chính:
- Chương giới thiệu: Cung cấp tổng quan về lý do chọn đề tài, mục tiêu, đối tượng, phạm vi nghiên cứu.
- Chương cơ sở lý thuyết: Định hình hệ thống kiến thức nền tảng về AI, Computer Vision, Edge AI và các framework phát triển Web.
- Chương thiết kế hệ thống: Đi sâu vào chi tiết kiến trúc của ứng dụng, cấu trúc mô hình mạng nơ-ron và luồng thông tin trong hệ thống Game Logic.
- Chương kết quả đạt được: Đưa ra các con số đánh giá từ thực nghiệm, hiệu năng phần cứng cũng như khả năng hoạt động ổn định của mạng lưới thiết bị.
- Chương kết luận: Tóm gọn lại các đóng góp nghiên cứu, thừa nhận các giới hạn của đồ án và đề xuất hướng phát triển dài hạn.
