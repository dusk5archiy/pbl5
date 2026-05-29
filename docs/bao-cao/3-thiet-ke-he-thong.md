# Thiết kế hệ thống

## Phân tích yêu cầu và kiến trúc tổng thể
Để đáp ứng mục tiêu số hóa tự động một ván cờ tương tác liên hệ vật lý, dự án đặt ra những yêu cầu kiến trúc phải đáp ứng ba vai trò độc lập (Services): Service phân tích không gian (AI), Service máy chủ trò chơi (Logic Game) và Service tiếp nhận hiển thị người dùng (Front-end GUI). Khung thiết kế tuân theo kiến trúc vi dịch vụ nhỏ (microservices-like modular architecture), trong đó các module không chia sẻ chung bộ nhớ trực tiếp mà giao tiếp nhau thông qua APIs và WebSockets.

Hệ thống được thiết kế với trung tâm là Máy chủ logic (Backend server chạy tại cổng 37001). Node Camera nhúng trên Raspberry PI (AI service tại cổng 8000) sẽ đóng vai trò là một client quan trọng độc lập, liên tục phân tích và truyền sự kiện đến Backend. Từng người chơi sẽ dùng trình duyệt (Next.js server cổng 3000) truy cập vào và đóng vai client mở luồng giao tiếp với Backend. 

## Thiết kế phân hệ Trí tuệ Nhân tạo (Khối AI)

Phân hệ AI chịu trách nhiệm xử lý luồng đa phương tiện hình ảnh từ camera, phân luồng theo chu kỳ thời gian (Time-series frame logic) và kết xuất dự đoán để ra kết quả mặt xúc xắc. 

### Thuật toán xác định chuyển động xúc xắc (Motion tracking & Frame difference)
Do xúc xắc cần một thời gian cuộn, nảy trên mặt bàn trước khi dừng cố định để đọc số, không thể tiến hành gọi liên tiếp mô hình suy luận sâu trên mọi khung hình quay được (giảm tuổi thọ thiết bị, tắc nghẽn CPU và kết quả vô nghĩa). Để giải quyết, quy trình thuật toán Frame Similarity được ứng dụng:
- Thu nhận khung ảnh theo chu kỳ.
- Phân tích sự chênh lệch biên độ điểm ảnh (pixel differences) và ma trận giữa khung liền trước (Previous Frame) và khung hiện tại (Current Frame). 
- Hệ số tương đồng `similarity_threshold` (theo cấu hình hệ thống là 0.5) được thiết lập. Nếu hình ảnh có mức thay đổi không lớn chứng tỏ xúc xắc đã dừng vật lý.
- Bộ đếm `consecutive_frames` tăng lên. Hệ thống quy định khi hai khung máy liên tiếp tĩnh (qualified_consecutive_frames = 2), AI mới chính thức kích hoạt pipeline nhận diện học sâu (Inference Pipeline). Quá trình này giúp mô hình giảm thiếu đến 85% tải điện toán không cần thiết.

### Thiết kế mô hình suy luận hai giai đoạn
Khối AI không dùng một mô hình đồng thời cả định vị và phân loại (vốn rất nặng) mà chia làm kịch bản hai bước chạy Pipeline (2-Stage cascaded pipeline) nhằm duy trì độ chuẩn theo khung nhẹ tối đa.
- **Stage 1 (Dice Detection):** Ảnh toàn màn từ camera được nén kích thước về chuẩn 640x480. Mô hình thiết kế dựa trên kiến trúc gốc YOLOv8 thu gọn (nano parameter scale) xuất ra định dạng model.tflite. Đặc trưng đầu ra là toạ độ hộp giới hạn (Bounding Boxes) xung quanh hai viên xúc xắc xuất hiện trong ống kính.
- **Stage 2 (Dice Score - Custom Score01 CNN):** Hệ thống tiến hành thao tác cắt xén vuông góc hình ảnh (Cropping) 2 vùng xúc xắc được gợi ý ở Stage 1 theo hệ tọa độ x, y, width, height. Mảnh ảnh này được phóng to cục bộ đưa thành kích thước chuẩn 32x32. Từ mảnh ảnh siêu nhỏ này, một mô hình phân loại (Classification Model) được thiết kế tùy biến, gọi là mạng Score01 (chỉ gồm tầng trích xuất Conv cơ bản, MaxPool và phân lớp Softmax), đánh giá khả năng lớp từ 1 đến 6 chấm trên mặt.
- Cuối cùng, tín hiệu hai mặt điểm xúc xắc tổng được gộp chung, khôi phục lại không gian gốc và mã hóa thành gói tin dạng JSON để bắn đi sự kiện.

## Thiết kế phân hệ Máy chủ (Backend Logic)
Lõi logic hệ thống xây dựng nhằm quản lý luật chơi Cờ Tỷ Phú bằng Python thuần kết nối WebSocket qua FastAPI. Máy chủ quản lý kiến trúc theo hướng Cây Trạng thái (Game State Tree). Toàn bộ bàn cờ được mô hình logic hóa các ô lưới.
Sơ đồ quản lý phân thành các Object chính:
- **GameState**: Thể hiện bức tranh toàn cảnh tại thời điểm bất kỳ, lưu trạng thái hiện hữu (GameLogicState) của các người chơi (LogicStatePlayer) như Tên, Tiền, Bất động sản sở hữu (BDS), Vị trí hiện tại trên bàn.
- **Action Tasks**: Là tập hợp các hàm tính toán biến đổi trạng thái từ chuỗi xử lý. Bao gồm tác vụ tung xúc xắc (`RollDiceTask`, `TripleDiceTask`), Mua đất (`BuyTask`), Trả tiền công ty (`PayTask`), Ngồi tù (`JailTask`) và Thẻ cớ hội/khí vận (`ActionCardTask`).  Khi sự kiện WebSocket AI (Roll Dice Result) đến, máy chủ gọi hàm cộng thêm số nước đi thay đổi tọa độ người chơi đang trong lượt, đồng thời kiểm tra sự kiện ô đó và sản sinh bộ lệnh (Chore Task) phản hồi.
- **GameDataManager**: Nhập liệu thông tin bản đồ, cấu hình tài sản ban đầu phân bổ cho cấu trúc trò chơi 4-6 người từ một hệ file JSON mô tả luật địa lý đất (games1.json).

## Thiết kế giao diện (Front-end Web)
Chữ ký thiết kế web của dự án sử dụng Next.js kết hợp luồng React. Phân giải cấu trúc UI thành các HOC (Higher-Order Components) tĩnh.
- **Socket Provider:** Giao tiếp trung ương lắng nghe `message` từ Back-end để điều phối state update qua Redux hoặc ContextAPI.
- **Bàn cờ trung tâm (Board UI):** Kết xuất màn hình trực quan các thẻ bài, được vẽ chuẩn CSS Grid linh hoạt (Tailwind CSS) bo dọc đường viền hiển thị trạng thái avatar người chơi khi nhảy ô vị trí.
- **Menu Quản trị:** Các bảng hiển thị tiền vốn, giao diện ra quyết định (Mua/bán), và quản lý kho chứa tài sản thẻ đất cho từng khung thông tin người dùng cụ thể. Toàn bộ thiết diện giao diện bảo đảm đặc tính thời gian thực ở độ trễ dưới 200 ms.
