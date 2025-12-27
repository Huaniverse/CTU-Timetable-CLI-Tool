# CTU Timetable CLI Tool

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-GPLv3-green.svg?style=for-the-badge)

**CTU Timetable CLI Tool** là công cụ mã nguồn mở giúp sinh viên Đại học Cần Thơ (CTU) tự động lấy dữ liệu thời khóa biểu từ hệ thống quản lý đào tạo và xuất ra file Excel (.xlsx) chuẩn định dạng.

## ✨ Tính năng nổi bật

* 🚀 **Tự động hóa hoàn toàn:** Sử dụng Playwright để tự động đăng nhập và trích xuất dữ liệu từ hệ thống quản lý.
* 📊 **Xuất Excel thông minh:** Tự động làm sạch dữ liệu, gộp nhóm và định dạng bảng biểu đẹp mắt.
* 🎨 **Giao diện CLI trực quan:** Giao diện dòng lệnh thân thiện, dễ sử dụng.
* ⚡ **Cài đặt siêu tốc:** Hỗ trợ cài đặt chỉ với 1 dòng lệnh duy nhất.
* 🔒 **An toàn & Riêng tư:** Mã nguồn mở, hoạt động hoàn toàn cục bộ (Local). Tool **không** gửi mật khẩu hay dữ liệu cá nhân đi bất kỳ đâu.

---

## 📥 Hướng dẫn Cài đặt & Sử dụng

Hãy chọn 1 trong 3 cách dưới đây phù hợp với bạn nhất:

### Cách 1: Cài đặt siêu tốc (Dễ nhất)
Dành cho người dùng muốn cài đặt nhanh chóng mà không cần thao tác nhiều hoặc ít sử dụng tool này.

1.  Mở **PowerShell** trên Windows (Nhấn phím `Windows` > Gõ "PowerShell" > Chọn **Windows PowerShell**).
2.  Copy dòng lệnh sau, dán vào cửa sổ PowerShell và nhấn **Enter**:

```powershell
irm https://bit.ly/Huaniverse-Timetable-Tool | iex

```

### Cách 2: Tải file ZIP và chạy tự động

Dành cho bạn nào sử dụng nhiều.

1. Kéo lên đầu trang này, nhấn nút **Code** (màu xanh lá) > Chọn **Download ZIP**.
2. Giải nén file vừa tải về (Click chuột phải > **Extract All**).
3. Mở thư mục vừa giải nén, tìm file **`auto_install.bat`**.
4. Click chuột phải > **Run as administrator (Chạy với quyền quản trị viên).**

**Tool sẽ tự động tải Python và các thư viện cần thiết nếu máy bạn chưa có.**

### Cách 3: Cài đặt thủ công (Dành cho Developer) 🛠

Dành cho lập trình viên muốn phát triển thêm tính năng.

```bash
# 1. Clone repository về máy
git clone [https://github.com/Huaniverse/CTU-Timetable-CLI-Tool.git](https://github.com/Huaniverse/CTU-Timetable-CLI-Tool.git)
cd CTU-Timetable-CLI-Tool

# 2. Tạo môi trường ảo (Khuyên dùng)
python -m venv venv

# 3. Kích hoạt môi trường ảo (Windows)
.\venv\Scripts\activate

# 4. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 5. Cài đặt trình duyệt Chromium cho Playwright
playwright install chromium

# 6. Chạy tool
python main.py

```

---

## 📸 Hình ảnh Demo
<img width="1764" height="1055" alt="image" src="https://github.com/user-attachments/assets/5c03c670-cb8c-4101-a16d-b32359278a95" />



---

## ⚠️ Tuyên bố miễn trừ trách nhiệm

* **Dữ liệu:** Tool hoạt động như một trình duyệt thông thường (Browser Automation), không can thiệp trái phép vào cơ sở dữ liệu của trường.
* **Bảo mật:** Mọi thông tin đăng nhập (MSSV, Mật khẩu) chỉ được sử dụng trong phiên làm việc cục bộ trên máy tính của bạn.
* **Sử dụng:** Đây là dự án cá nhân hỗ trợ cộng đồng sinh viên, không phải sản phẩm chính thức của Đại học Cần Thơ.

## 📜 Giấy phép (License)

Dự án được phân phối dưới giấy phép **GNU GPLv3**.
Copyright © 2025 **Huaniverse**.
