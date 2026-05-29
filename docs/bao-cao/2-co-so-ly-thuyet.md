# Cơ sở lý thuyết

## Tổng quan về trò chơi số hóa
Việc tự động hóa và số hóa các trò chơi cờ bàn truyền thống đòi hỏi một hệ thống có khả năng chuyển đổi các sự kiện vật lý (như đổ xúc xắc, di chuyển quân cờ) thành trạng thái dữ liệu kỹ thuật số. Cờ tỷ phú (Monopoly) đặc thù là trò chơi phụ thuộc vào cơ chế ngẫu nhiên từ 2 viên xúc xắc lục diện. Để tạo ra sự liên kết giữa tương tác vật lý (đổ xúc xắc thật) với hệ thống ảo (tính toán nước đi hiện tại, tiền bạc), người ta cần một bộ trung gian đóng vai trò như cửa ngõ thu nhận dữ liệu không gian, từ đó hình thành hướng nghiên cứu bằng thị giác máy tính.

## Thị giác máy tính và phân tích hình ảnh không gian
Thị giác máy tính (Computer Vision) là một nhánh của trí tuệ nhân tạo, nghiên cứu cách để trang bị cho máy móc năng lực nhìn và hiểu hình ảnh không gian tương tự như con mắt của con người. Đối với hệ thống này, hai quá trình cốt lõi trong thị giác máy tính được áp dụng là: Phát hiện đối tượng (Object Detection) và Nhận dạng đối tượng (Object Classification). 
Phát hiện đối tượng nhằm trả lời cho câu hỏi: "Ở đâu trong bức ảnh này chứa xúc xắc?" và định vị chúng thông qua Hộp giới hạn (Bounding Boxes). Nhận dạng đối tượng là việc đưa các lớp bounding box đã được trích xuất phân tích chi tiết: "Mặt xúc xắc này có bao nhiêu chấm đen?". Sức mạnh của thị giác máy tính hiện đại phụ thuộc phần lớn vào Mạng nơ-ron tích chập (Convolutional Neural Networks - CNNs).

## Mạng nơ-ron học sâu tích chập (CNN)
CNN là một lớp của mạng nơ-ron sâu được thiết kế chuyên biệt để phân tích dữ liệu dạng lưới hai chiều như hình ảnh. Các nơ-ron trong mô hình CNN được tổ chức theo chiều không gian (rộng, cao, sâu) và xử lý liên tiếp thông qua ba loại lớp chính:
- Convolutional Layer (Lớp tích chập): Áp dụng các bộ lọc (filters/kernels) trượt dọc trên hình ảnh để tạo ra các bản đồ đặc trưng (feature maps), giúp giữ lại cấu trúc không gian của hình ảnh như đường viền, góc cạnh, hay các dạng hình học cụ thể (chấm tròn của xúc xắc).
- Pooling Layer (Lớp gộp): Giảm kích thước không gian của bản đồ đặc trưng nhằm giảm số lượng tham số tính toán, kiểm soát hiện tượng quá khớp (overfitting), tiêu biểu nhất là phương pháp Max Pooling.
- Fully Connected Layer (Lớp liên kết chéo): Được đặt ở cuối mạng lưới sau khi đã trải phẳng (flatten) các đặc trưng trích xuất, để thực hiện dự đoán một chuỗi điểm tương ứng với bài toán phân loại hoặc hồi quy tọa độ.

## Kiến trúc YOLO trong học thị giác
YOLO (You Only Look Once) là một khung kiến trúc học sâu tiên phong thay đổi cách thức phát hiện đối tượng với cơ chế End-to-End. Khác với các mô hình two-stage như R-CNN (cần đề xuất vùng Region Proposals sau đó mới phân loại), YOLO xử lý hình ảnh như một bài toán hồi quy (regression problem) liền mạch bằng cách chia hình ảnh đầu vào thành một mạng lưới dạng S x S grid. Mỗi ô grid chịu trách nhiệm dự đoán các hộp giới hạn, tỷ lệ tin cậy (confidence scores) và xác suất của lớp. Bằng cách chỉ "nhìn một lần" toàn bộ hình ảnh, YOLO mang tới tốc độ rất cao (real-time performance) mà vẫn duy trì độ chính xác (Precision/Recall) ấn tượng, vô cùng lý tưởng đối với các hệ thống nhúng.

## Edge AI và TensorFlow Lite
Edge AI - Trí tuệ nhân tạo tại biên, là xu hướng đang lên thông qua việc đặt trực tiếp mô hình phân tích sâu vào máy tính nhúng tại nơi phát sinh dữ liệu, thay vì gửi dữ liệu gốc (ảnh thô) về đám mây xử lý. Việc cài đặt trên Raspberry Pi 4 cho hệ thống này giúp loại bỏ hoàn toàn độ trễ đường truyền băng thông cao, đảm bảo tính bảo mật cục bộ nhưng lại đối mặt với bài toán tối ưu về cả bộ nhớ và năng lực tính toán không có GPU (Graphics Processing Unit). 

Để khắc phục, TensorFlow Lite (TFLite) ra đời. Nó là bộ phần mềm nhẹ mã nguồn mở thuộc hệ sinh thái TensorFlow chuyên phân phối cho thiết bị di động và nhúng. TFLite chuyển đổi mô hình học sâu mặc định thành tệp cấu trúc nén dung lượng rất thấp thông qua các thuật toán: Lượng tử hóa trọng số (Quantization) – giảm biểu diễn float32 xuống int8, và Cắt tỉa mô hình (Pruning), dẫn đến sự gia tốc gấp nhiều lần các phép tính chập trên các tập cấu hình CPU ARM.

## Cơ chế hướng sự kiện và giao thức truyền tải WebSocket
Khác biệt hoàn toàn so với mô hình HTTP truyền thống là Client tuần tự gửi request (yêu cầu) và Server trả lại response (phản hồi), trò chơi Cờ tỷ phú là tập hợp liên hoàn vòng lặp theo trạng thái của nhiều người tham gia và của sự kiện kết xuất ra từ camera. Việc đảm bảo các bên (Camera Pi, Máy chủ, Player) đều nắm được trạng thái mới nhất cần kết nối hai chiều liên tục.
WebSocket giải quyết trọn vẹn đặc tính này bẳng cách thiết lập một phiên nối liền (TCP handshake) duy trì mở vĩnh viễn (Persistent connection) sau khi kết nối. Mọi thực thể ở các tầng khác nhau trong mạng (Front-end browser của máy tính con, Back-end API game server) đều nhận và cập nhật UI ngay lập tức khi Trí tuệ nhân tạo bắn tín hiệu "Có một xúc xắc được cập nhật".

Tích hợp với nguyên lý này là thư viện FastAPI (Backend) trên nền ngôn ngữ Python, mang lại độ song song hóa chuẩn xác bằng asyncio và React/Next.js cho Frontend để ánh xạ dữ liệu trực quan lên trình duyệt.
