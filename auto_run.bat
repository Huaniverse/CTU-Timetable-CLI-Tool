@echo off
setlocal enabledelayedexpansion

:: --- QUAN TRỌNG: Chuyển về thư mục hiện tại của file BAT ---
cd /d "%~dp0"

:: Tắt chế độ Quick Edit để tránh click chuột làm treo tool
powershell -command "&{$H=get-host;$W=$H.ui.rawui;$O=$W.options;$O.quickeditmode=$false;$W.options=$O;}" >nul 2>&1

:: Chuyển mã sang UTF-8 để hiển thị tiếng Việt
chcp 65001 >nul

:: --- THIẾT LẬP MÀU SẮC (ANSI COLORS) ---
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "ESC=%%b"
)

set "RESET=%ESC%[0m"
set "BOLD=%ESC%[1m"
set "RED=%ESC%[31m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "MAGENTA=%ESC%[35m"
set "CYAN=%ESC%[36m"
set "WHITE=%ESC%[37m"
set "BG_RED=%ESC%[41m"

title HUANIVERSE TIMETABLE TOOL - AUTO INSTALLER
cls

:: --- BANNER ---
echo.
echo  %CYAN%╔════════════════════════════════════════════════════════════╗%RESET%
echo  %CYAN%║%BOLD%%WHITE%            HUANIVERSE TIMETABLE TOOL -  AUTO RUN           %RESET%%CYAN%║%RESET%
echo  %CYAN%╚════════════════════════════════════════════════════════════╝%RESET%
echo.
echo  %BOLD%Chào bạn! Tool đang chuẩn bị môi trường chạy tốt nhất cho bạn...%RESET%
echo.

:: --- BƯỚC 1: KIỂM TRA PYTHON ---
echo  %MAGENTA%[Bước 1/4]%RESET% Kiểm tra Python...

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo    %GREEN% Đã tìm thấy Python trên máy tính.%RESET%
    set "PYTHON_EXEC=python"
    goto :PYTHON_OK
)

echo    %YELLOW% Máy bạn chưa có Python.
echo    Đang tải xuống phiên bản 3.11...%RESET%
curl -o python_installer.exe https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe

if not exist python_installer.exe (
    goto :ERROR_NETWORK
)

echo    %YELLOW% Đang cài đặt Python (Khoảng 1-2 phút)...%RESET%
echo    %RED% VUI LÒNG KHÔNG TẮT CỬA SỔ NÀY!%RESET%
python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
del python_installer.exe

:: Cập nhật đường dẫn tạm thời và GÁN ĐƯỜNG DẪN CỨNG
set "PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"
set "PYTHON_EXEC=C:\Program Files\Python311\python.exe"

if not exist "!PYTHON_EXEC!" (
    echo    %BG_RED%[LỖI]%RESET% %RED%Cài đặt Python thất bại hoặc đường dẫn khác mặc định.%RESET%
    goto :ERROR
)

echo    %GREEN% Cài đặt Python thành công!%RESET%

:PYTHON_OK
echo.

:: --- BƯỚC 2: TẠO MÔI TRƯỜNG ẢO ---
echo  %MAGENTA%[Bước 2/4]%RESET% Kiểm tra Môi trường ảo (Virtual Env)...

if exist "venv\Scripts\activate.bat" (
    echo    %GREEN% Môi trường ảo đã tồn tại.%RESET%
    goto :VENV_OK
)

echo    %CYAN% Đang tạo môi trường ảo để giữ sạch máy tính...%RESET%
:: Sử dụng biến PYTHON_EXEC để gọi đúng file vừa cài
"!PYTHON_EXEC!" -m venv venv
if %errorlevel% neq 0 (
    echo    %BG_RED%[LỖI]%RESET% %RED%Không thể tạo venv. Hãy thử chạy với quyền Admin.%RESET%
    goto :ERROR
)
echo    %GREEN% Tạo môi trường thành công.%RESET%

:VENV_OK
echo.

:: --- BƯỚC 3: CÀI ĐẶT THƯ VIỆN ---
echo  %MAGENTA%[Bước 3/4]%RESET% Kiểm tra thư viện...

if not exist "requirements.txt" (
    echo    %BG_RED%[LỖI]%RESET% %RED%Không tìm thấy file 'requirements.txt'.%RESET%
    echo    %YELLOW%Vui lòng đảm bảo file này nằm cùng thư mục với file cài đặt.%RESET%
    goto :END_ERROR
)

echo    %CYAN% Đang cài đặt/cập nhật thư viện...%RESET%
call venv\Scripts\activate

:: Đã bỏ >nul để hiện lỗi nếu có
pip install -r requirements.txt --disable-pip-version-check -q

if %errorlevel% neq 0 (
    echo.
    echo    %BG_RED%[LỖI]%RESET% %RED%Cài đặt thư viện thất bại.%RESET%
    goto :ERROR
)
echo    %GREEN% Thư viện đã sẵn sàng.%RESET%
echo.

:: --- BƯỚC 4: CÀI BROWSER PLAYWRIGHT ---
echo  %MAGENTA%[Bước 4/4]%RESET% Kiểm tra trình duyệt Chromium...

if exist "venv\browser_installed.marker" (
    echo    %GREEN% Trình duyệt đã được cài đặt từ trước.%RESET%
    goto :RUN_TOOL
)

echo    %YELLOW% Đây là lần chạy đầu tiên, đang tải trình duyệt...%RESET%
echo    %YELLOW% File nặng khoảng 100MB, vui lòng đợi...%RESET%
playwright install chromium
if %errorlevel% neq 0 (
    goto :ERROR_NETWORK
)

echo installed > "venv\browser_installed.marker"
echo    %GREEN% Tải trình duyệt thành công!%RESET%

:RUN_TOOL
echo.
echo  %BOLD%%GREEN%TẤT CẢ ĐÃ SẴN SÀNG - ĐANG KHỞI ĐỘNG TOOL
echo.
:: Chạy file main
python main.py

if exist "KetQua_Excel" (
    start "" "KetQua_Excel"
) else (
    explorer .
)
goto :END

:ERROR_NETWORK
echo.
echo  %BG_RED%[LỖI KẾT NỐI]%RESET% %RED%Không thể tải xuống dữ liệu.%RESET%
echo  %YELLOW%Vui lòng kiểm tra lại mạng Internet và thử lại.%RESET%
goto :END_ERROR

:ERROR
echo.
echo  %BG_RED%[LỖI NGHIÊM TRỌNG]%RESET% %RED%Đã có lỗi xảy ra trong quá trình cài đặt.%RESET%
echo  %YELLOW%Hãy chụp màn hình này và gửi cho tác giả.%RESET%

:END_ERROR
color 40
pause
exit

:END
echo  %CYAN%Cảm ơn bạn đã sử dụng! Nhập phím bất kỳ để thoát%RESET%

pause >nul
