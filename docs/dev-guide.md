# Dev Guide

Cập nhật lúc: 18-01-2026

## Tổng quan

Dự án (tính tới lúc cập nhật bài viết) được chia làm 3 thành phần

- AI: Huấn luyện và triển khai mô hình AI
- Back: Đảm nhận xử lí thông tin trong hệ thống
- Front: Giao diện của hệ thống

**Thư mục gốc** của dự án có tệp `requirements.txt` chứa tên
các thư viện Python dùng cho tất cả các thành phần khi triển khai.

Mỗi thành phần còn có riêng một tệp `requirements.txt` chứa tên
các thư viện Python dùng cho riêng thành phần đó trong quá trình phát triển.

## Hướng dẫn chung cho tất cả các thành phần

**Lưu ý**

- Dùng Git Bash làm shell mặc định trên VS Code.
- Có `python` (và `node` đối với front-end) được thêm vào PATH.
- Bất kì file `.sh` nào trong các thư mục `scripts` cũng đều nên đọc qua.
- Khi triển khai (production), cần phải mở trình soạn thảo trong thư mục gốc
của dự án.

Chạy lệnh sau để tiến hành thiết lập các thư viện và biên dịch front-end:

```bash
scripts/wsetup.sh
```

dùng lệnh sau để chạy toàn bộ hệ thống:

```bash
scripts/wrun.sh start
```

## Phần AI

Khi phát triển (dev), cần phải mở trình soạn thảo trong thư mục `ai`,
không phải thư mục gốc của dự án.

Phần AI dùng để huấn luyện các mô hình và triển khai chúng qua các API.

Việc huấn luyện AI có thể được thực hiện trên các máy có GPU. Tuy nhiên,
khi triển khai thì phải chạy trên CPU, để mô phỏng hạn chế của phần cứng 
Raspberry Pi.

Khi mới bắt đầu clone dự án về để dev, chạy lệnh sau để thiết lập môi trường
phát triển:

```bash
# Bạn phải đảm bảo rằng mình đang đứng tại thư mục `ai`
scripts/setup.sh
```
Bước vào môi trường ảo:

```bash
. scripts/venv.sh
```

Huấn luyện các mô hình:

```bash
scripts/train.sh
```

## Phần Back

Khi phát triển (dev), cần phải mở trình soạn thảo trong thư mục `back`,
không phải thư mục gốc của dự án.

Khi mới bắt đầu clone dự án về để dev, chạy lệnh sau để thiết lập môi trường
phát triển:

```bash
# Bạn phải đảm bảo rằng mình đang đứng tại thư mục `back`
scripts/setup.sh
```
Bước vào môi trường ảo:

```bash
. scripts/venv.sh
```

## Phần Front

Khi phát triển (dev), cần phải mở trình soạn thảo tại thư mục gốc của dự án.

Chạy lệnh sau để tải về các thư viện và biên dịch front-end:

```bash
scripts/wsetup.sh
```

dùng lệnh sau để phát triển:

```bash
scripts/wrun.sh
```
---
