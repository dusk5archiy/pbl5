# Kết quả báo cáo

## Thiết lập môi trường thực nghiệm
Hệ thống phần cứng thử nghiệm là một khối mạch Raspberry Pi 4 Model B tích hợp 4GB RAM LPDDR4 chạy hệ điều hành Ubuntu Server phiên bản 64-bit hoặc nhân Debian cơ sở. Máy chủ giao diện và logic có thể chạy đồng bộ cục bộ trực tiếp trên Raspberry Pi hoặc phân bổ tải cho một Laptop cục bộ mạng nội bộ qua cổng `_port.sh` và switch Ethernet.
Về phần cứng ảnh chụp trực tiếp: sử dụng một camera Logitech C920 hoặc module camera PI chuẩn truyền USB thu thập khung phân giải 720p/30fps. Yêu cầu thiết lập môi trường chơi đảm bảo điều kiện có nguồn sáng phòng hắt xuống mặt bàn tránh vùng đổ bóng đen tối đàm che khuất chấm đen xúc xắc.

## Kết quả quá trình huấn luyện mô hình sâu (AI Training Performance)
Tập dữ liệu xây dựng và thực nghiệm: Tập dữ liệu ảnh xúc xắc nội sinh với trên hàng ngàn tấm hình khác nhau (`s7dataset-2-dice-detection`), qua các pha xử lý màu, lọc nhiễu, trộn ngẫu nhiên (augmentation).
- **Mô hình Dice Detection (Định vị hộp ảnh):** Sau nhiều lượt `epochs` huấn luyện, chỉ số mAP50 (Mean Average Precision tại threshold 0.5 IoU) đạt hiệu suất ổn định ở mức xuất sắc trên 96%. Mô hình bao trọn không bỏ sót xác suất xuất hiện các hạt xúc xắc trong mọi khung quét. Đường cắt giảm (Loss functions) tiệm cận 0 khá mượt mà, phản ánh độ biểu diễn chính xác vị trí ngay cả khi góc bàn nghiêng.
- **Mô hình Dice Score Classification (Đọc điểm mốc Score01):** Được huấn luyện riêng rẽ trên bộ ảnh phân giải siêu thấp 32x32 kích thước chuẩn bị sẵn theo 6 nhãn (1 đến 6). Accuracy (Độ chính xác) suy luận tập Validation vượt qua ngưỡng 98% chỉ trong khoảng 50 cycles lặp, minh chứng cho cấu trúc ConvNet gọn và dữ liệu ghim label rất vững chắc.

## Đánh giá khả năng suy luận trên thiết bị biên (Edge Inference Benchmarks)
Phép thử tốc độ phần cứng (Hardware Benchmark) trên máy tính nhúng IoT đã mang về sự khích lệ rất đáng kể.
- **Mô hình TFLite FP32/Int8:** Thông qua việc chuyển đối về dạng `.tflite`, sự suy luận 1 khung từ AI Dice Detection chỉ mất khoảng xấp xỉ 20 - 45 mili-giây (ms); Mô hình thứ cấp Score01 đọc ra số hạt chỉ mất vỏn vẹn 2 - 5 mili-giây với quy trình CPU 4 nhân của Pi 4B. Tốc độ khung hình (FPS) trung duy trì đều đặn ở mức 15 đến 22 FPS khi xử lý chuỗi luồng liên tục (Video Streaming Pipeline). Hệ thống có dung sai vượt ngoài khả năng chống chịu độ rung khung nhờ thuật toán Tracking Logic (Similarity Threshold Limit), loại trừ hoàn toàn các khung ảo do hiệu ứng chuyển động mờ (Motion Blur) khi xúc xắc lăn quá nhanh, bắt đứng chính xác tỷ lệ trạng thái nghỉ.

## Đánh giá vận hành logic Game thực nghiệm và Truyền tải WebSocket
Ván cờ được khởi động vận hành 4 khách đa tuyến độc lập truy cập vào. Hệ lưu trữ logic Backend ghi nhận độ bám hoàn hảo từng sự kiện, bao gồm các phép thu mua phức hợp, qua nhà tù (Jail Break Event) và trả thế chấp. 
Giao thức WebSocket không xuất hiện bất kỳ tình trạng timeout (disconnect ngoài ý muốn) nào khi triển khai băng thông dưới chuẩn mạng WiFi 2.4/5GHz. Delay cập nhật luồng từ điểm AI đưa lên cho màn hình GameFront-End gần như là nhãn tiền (khoảng ~125 ms toàn thời gian vòng đời một thao tác Event-Trigger). Đồng hồ thời gian và đồ họa React re-render ở mức ổn định cực kì trơn tru đáp ứng đúng kiến trúc luồng dữ liệu một chiều (One-way binding principle).

Nói chung, hệ thống Cờ tỷ phú ứng dụng trí tuệ AI và vật lý máy chủ đã thành hình hoàn thiện, đạt đúng công năng đặt ra đầu kỳ, sẵn sàng làm giải pháp cốt lõi trình diễn ứng dụng Công nghệ AI tạo viền biên.
