# Cài đặt kiosk trên Minimized Ubuntu Server

## Start và Enable daemon `snapd`

```bash
sudo systemctl start snapd
sudo systemctl enable snapd
```

Kiểm tra trạng thái hoạt động của `snapd`:

```bash
sudo systemctl status snapd
```

## Tải về các gói chương trình

```bash
sudo snap install ubuntu-frame
sudo snap set ubuntu-frame daemon=true
sudo snap install chromium
sudo snap set chromium url=...
sudo snap set chromium daemon=true
snap connect chromium:wayland
```

Kiểm tra trạng thái bằng lệnh `snap services`.

Chuyển URL:

```bash
sudo snap set chromium url=...
sudo snap restart chromium
```

## Tự động đăng nhập
