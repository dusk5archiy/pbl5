# Cài đặt trên Minimized Ubuntu Server

Cập nhật lúc: 18-01-2026.

## Cài đặt Minimized Ubuntu Server

Tải file .iso Ubuntu Server dựa trên các thông tin sau:

- Phiên bản `24.04.3 LTS`.
- [Link tải Ubuntu Server](https://ubuntu.com/download/server)

Trong quá trình cài đặt:

- Phải có màn hình hiển thị
- Chọn cài Minimized Ubuntu Server
- Có kết nối internet
- Chọn cài OpenSSH

Sau khi đã cài đặt hệ điều hành thành công, ta sẽ tiến hành clone dự án vào máy.

## Cài đặt repo dự án

Tải `git` bằng lệnh sau:

```bash
sudo apt install git
```

sau đó, clone repo này vào thư mục `~`, rồi thiết lập như sau:

```bash
cd ~
git clone https://github.com/dusk5archiy/pbl5.git
cd pbl5
chmod +x scripts/*
scripts/usetup.sh
```

Sau khi thiết lập xong, khởi động lại máy bằng lệnh:

```bash
sudo reboot
```
Sau khi khởi động lại xong, chương trình sẽ tự động được chạy.
