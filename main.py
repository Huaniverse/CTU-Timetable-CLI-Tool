"""
PROJECT: Huaniverse Timetable Tool (SchedBot Core)
AUTHOR: Nguyen Le Huu Huan (Huaniverse)
DESCRIPTION: 
    Tool hỗ trợ cào dữ liệu thời khóa biểu/lịch học từ hệ thống Đăng ký môn học của ĐH Cần Thơ (CTU).
    Sử dụng Playwright để tự động hóa trình duyệt và Pandas để xuất dữ liệu ra Excel.
"""

import re
import sys
import time
import os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright
from colorama import Fore, Style, init
import pwinput

# Kiểm tra thư viện quản lý cửa sổ (chỉ chạy trên Windows)
try:
    import pygetwindow as gw
except ImportError:
    print("Vui lòng cài đặt thư viện: pip install pygetwindow")
    sys.exit(1)

# Khởi tạo colorama để in màu trên terminal
init(autoreset=True)

BANNER = r"""
┌───────────────────────────────────────────────────────────────┐
│                   Huaniverse Timetable Tool                   │
└───────────────────────────────────────────────────────────────┘
"""

# ==============================================================================
# PHẦN 1: CÁC HÀM TIỆN ÍCH GIAO DIỆN (UI & UTILITIES)
# ==============================================================================

def rgb_text(r, g, b, text):
    """Tạo màu text RGB tùy chỉnh cho terminal."""
    return f"\033[1;38;2;{r};{g};{b}m{text}"

def print_gradient(text):
    """
    In text với hiệu ứng gradient (chuyển màu từ xanh dương sang xanh ngọc).
    Giúp giao diện CLI trông hiện đại hơn.
    """
    lines = [line for line in text.split('\n') if line]
    if not lines: return

    max_width = max(len(line) for line in lines)
    start_color = (0, 139, 255)  # Xanh dương đậm
    end_color = (95, 255, 236)   # Xanh ngọc sáng

    for line in lines:
        colored_line = ""
        for i, char in enumerate(line):
            ratio = i / max_width if max_width > 0 else 0
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            colored_line += rgb_text(r, g, b, char)
        print(Style.BRIGHT + colored_line + Style.RESET_ALL)

# ==============================================================================
# PHẦN 2: HÀM KIỂM TRA DỮ LIỆU ĐẦU VÀO (VALIDATORS)
# ==============================================================================

def validate_academic_year(year: str) -> bool:
    """Kiểm tra định dạng năm học (VD: 2025-2026 hoặc 25-26)."""
    return bool(re.match(r"^(\d{4}-\d{4})|(\d{2}-\d{2})$", year))

def validate_semester(sem: str) -> bool:
    """Kiểm tra học kỳ (chỉ chấp nhận 1, 2, 3)."""
    return sem in ["1", "2", "3"]

def validate_course_code(code: str) -> bool:
    """Kiểm tra định dạng mã học phần (VD: CT123, ML001)."""
    return bool(re.match(r"^[A-Z]{2}\d{3}E?$", code))

# ==============================================================================
# PHẦN 3: QUẢN LÝ CỬA SỔ TRÌNH DUYỆT
# ==============================================================================

def minimize_browser_window():
    """
    Thu nhỏ cửa sổ trình duyệt xuống taskbar để không che khuất terminal.
    Hỗ trợ trải nghiệm người dùng tốt hơn khi chạy chế độ headless=False.
    """
    try:
        time.sleep(0.2) 
        windows = []
        # Tìm cửa sổ Chrome/Chromium
        for title in ['Chromium', 'Chrome', 'Google Chrome']:
            windows = gw.getWindowsWithTitle(title)
            if windows: break
        
        if windows and not windows[0].isMinimized:
            windows[0].minimize()
    except Exception:
        pass

# ==============================================================================
# PHẦN 4: CHƯƠNG TRÌNH CHÍNH (MAIN EXECUTION)
# ==============================================================================

def run(playwright):
    # Xóa màn hình console khi bắt đầu
    os.system('cls' if os.name == 'nt' else 'clear')
    print_gradient(BANNER)

    all_data = {"courses": {}}
    academic_year = ""
    semester = ""
    
    # -----------------------------------------------------------
    # BƯỚC 1: CẤU HÌNH THÔNG TIN CẦN LẤY
    # -----------------------------------------------------------
    print_gradient("                       CẤU HÌNH THÔNG TIN")

    # Vòng lặp nhập năm học
    while True:
        academic_year = input(Fore.MAGENTA + " Nhập năm học (ví dụ 25-26 hoặc 2025-2026): " + Fore.WHITE)
        if validate_academic_year(academic_year):
            # Chuẩn hóa về dạng đầy đủ YYYY-YYYY
            if len(academic_year) == 5:
                p1, p2 = academic_year.split("-")
                if int(p1) < int(p2):
                    academic_year = f"20{p1}-20{p2}"
                else:
                    print(Fore.RED + " Năm học không hợp lệ")
                    continue
            break
        print(Fore.RED + " Năm học không hợp lệ.")

    # Vòng lặp nhập học kỳ
    while True:
        semester = input(Fore.MAGENTA + " Nhập học kỳ (1,2,3): " + Fore.WHITE)
        if validate_semester(semester): break
        print(Fore.RED + " Học kỳ phải là số 1, 2 hoặc 3")

    # Vòng lặp nhập mã học phần
    while True:
        course_input = input(Fore.MAGENTA + " Nhập các mã học phần (cách nhau bằng dấu phẩy): " + Fore.WHITE)
        course_codes = [code.strip().upper() for code in course_input.split(",") if code.strip()]
        if all(validate_course_code(code) for code in course_codes): break
        print(Fore.RED + " Mã học phần không hợp lệ.")

    # -----------------------------------------------------------
    # BƯỚC 2: ĐĂNG NHẬP HỆ THỐNG (SSO CTU)
    # -----------------------------------------------------------
    browser = None
    page = None
    context = None

    while True: # Vòng lặp retry đăng nhập nếu sai mật khẩu
        
        # --- UI: Vẽ lại màn hình đăng nhập ---
        os.system('cls' if os.name == 'nt' else 'clear') 
        print_gradient(BANNER)
        
        # Hiển thị lại các thông tin đã cấu hình
        print_gradient("                        CẤU HÌNH THÔNG TIN")
        print(Fore.MAGENTA + " Năm học: " + Fore.WHITE + academic_year)
        print(Fore.MAGENTA + " Học kỳ: " + Fore.WHITE + semester)
        print(Fore.MAGENTA + " Mã học phần: " + Fore.WHITE + ", ".join(course_codes))
        
        print_gradient("─────────────────────────────────────────────────────────────────")
        print_gradient("                            ĐĂNG NHẬP")

        # Nhập credentials (Mật khẩu được ẩn bằng pwinput)
        username = input(Fore.CYAN + Style.BRIGHT + " Nhập MSSV: " + Fore.WHITE)
        password = pwinput.pwinput(prompt= Fore.CYAN + " Nhập mật khẩu: ", mask= "•")
        
        print_gradient("─────────────────────────────────────────────────────────────────")
        print(Fore.YELLOW + " Đang khởi động trình duyệt...", end="\r")
        
        # Khởi tạo browser (headless=False để xử lý các redirect phức tạp của SSO)
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        page = context.new_page()

        minimize_browser_window() # Ẩn browser

        try:
            # Truy cập trang Login
            page.goto("https://htql.ctu.edu.vn/htql/login.php")
            page.fill("#usernameUserInput", username) 
            page.fill("#password", password)
            
            # Click đăng nhập
            page.click("#sign-in-button")
            
            # Hard wait 5s để hệ thống xử lý (CTU server response time thay đổi thất thường)
            print(Fore.YELLOW + " Đang đăng nhập..." + " "*20, end="\r")
            page.wait_for_timeout(5000) 
            
            current_url = page.url
            
            # --- KIỂM TRA KẾT QUẢ ĐĂNG NHẬP ---
            if "authFailure=true" in current_url or "authenticationendpoint/login.do" in current_url:                
                # Trường hợp sai mật khẩu
                browser.close()
                for i in range(3, 0, -1):
                    print(Style.BRIGHT + Fore.RED + f"\r [SAI MẬT KHẨU] Vui lòng kiểm tra lại MSSV hoặc Mật khẩu sau {i}",  end="\r")
                    time.sleep(1)
                time.sleep(1)
                continue # Quay lại nhập lại mật khẩu
            
            elif "hindex.php" in current_url:
                # Đăng nhập thành công (redirect về trang chủ sinh viên)
                print(Fore.GREEN + " Đăng nhập thành công", end=" ")
                break 
            
            else:
                print(Fore.YELLOW + "\r Cảnh báo: Trạng thái không xác định. Đang thử tiếp tục...", end="")
                break

        except Exception as e:
            login_error_message = f" Lỗi kết nối: {e}"
            print(Fore.YELLOW + " Đang thử lại...")
            if browser: browser.close()
            continue

    # -----------------------------------------------------------
    # BƯỚC 3: CÀO DỮ LIỆU TỪ TRANG ĐĂNG KÝ HỌC PHẦN
    # -----------------------------------------------------------
    try:
        # Điều hướng sang trang Đăng ký môn học (DKMH)
        page.goto("https://dkmh.ctu.edu.vn/htql/sinhvien/hindex.php")
        print(Fore.GREEN + "--> dkmh.ctu.edu.vn", end = " ")
        
        # Xử lý redirect giữa hệ thống cũ và mới (dkmh vs dkmhfe)
        link_dk = page.locator("img[onclick='gotoDKindex()']")
        if link_dk.is_visible():
            link_dk.click()
        else:
            page.goto("https://dkmhfe.ctu.edu.vn/dangkyhocphan/sinhvien/quydinhdangky")
        
        page.wait_for_url("**/dangkyhocphan/sinhvien/quydinhdangky", timeout=10000)
        print(Fore.GREEN + "--> dkmhfe.ctu.edu.vn")
        
        # Mở danh mục học phần
        page.click("text=Danh mục học phần")
        page.wait_for_selector("#rc_select_0", state="visible")

        # Lưu metadata
        all_data["academic_year"] = academic_year
        all_data["semester"] = semester

        # Điền Năm học & Học kỳ vào dropdown filter
        page.fill("#rc_select_0", academic_year)
        page.keyboard.press("Tab")
        page.keyboard.type(semester)

        # Loop qua từng mã học phần để lấy dữ liệu
        for course_code in course_codes:
            print(Fore.YELLOW + f" Đang lấy dữ liệu học phần {course_code}..." + " "*20,end = "\r")

            # Xóa input cũ và điền mã mới
            page.click("#rc_select_2") 
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            
            page.fill("#rc_select_2", course_code)
            page.click("span[aria-label='search']")
            page.wait_for_timeout(1500) # Đợi API load dữ liệu

            # Lấy tên đầy đủ của môn học
            course_name = "N/A"
            try:
                name_elem = page.locator("p:has-text('Danh mục học phần:')").first
                if name_elem.is_visible():
                    raw_text = name_elem.inner_text().strip()
                    text_processing = raw_text.replace("Danh mục học phần:", "").strip()
                    if "(Mã:" in text_processing:
                        course_name = text_processing.split("(Mã:")[0].strip()
                    else:
                        course_name = re.sub(r'\s*\([^()]*\)', '', text_processing).strip()
            except Exception:
                pass

            # Logic xử lý bảng (Table Scraping)
            final_data = []
            current_group = None # Biến giữ giá trị Nhóm học phần (để xử lý merged cell)
            page_index = 1

            while True:
                try:
                    # Đợi bảng load xong
                    page.wait_for_selector("tbody.ant-table-tbody tr", timeout=3000)
                    rows = page.locator("tbody.ant-table-tbody tr")
                    count = rows.count()

                    if count == 0: break

                    # Lấy raw text từ các ô
                    raw_data = []
                    for i in range(count):
                        cells = rows.nth(i).locator("td")
                        row_data = [cells.nth(j).inner_text().strip() for j in range(cells.count())]
                        if row_data: raw_data.append(row_data)

                    # Chuẩn hóa dữ liệu: Xử lý trường hợp dòng bị thiếu cột do merged cells
                    normalized_data = []
                    for row in raw_data:
                        # Nếu dòng đủ 25 cột (dòng đầu tiên của nhóm), cấu trúc đầy đủ
                        # Nếu thiếu, thường là do cột Nhóm/Mã lớp đã bị merge -> Cần fill
                        if len(row) == 25: 
                            row.insert(0, "")
                            row.insert(0, "")
                        normalized_data.append(row)

                    # Map dữ liệu vào dict
                    for row in normalized_data:
                        # Logic fill-down cho cột "Nhóm" (nếu ô trống, lấy giá trị của dòng trên)
                        if len(row) > 0 and row[0] != "":
                            current_group = prev_group = row[0]
                        else:
                            current_group = prev_group
                        
                        get_col = lambda idx: row[idx] if len(row) > idx else "N/A"
                        
                        final_data.append({
                            "Mã học phần": course_code,
                            "Tên học phần": course_name,
                            "Nhóm": current_group,
                            "Thứ": get_col(2),
                            "Tiết học": re.sub(r'-', '', get_col(6)), # Xóa dấu gạch nối trong tiết
                            "Phòng": get_col(7),
                            "Sĩ số": f"{get_col(5)}/{get_col(4)}" if get_col(5) != "N/A" else "N/A",
                            "Giảng viên": row[-1] if len(row) > 0 else "N/A"
                        })

                    # Xử lý phân trang (Pagination)
                    next_button = page.locator("li.ant-pagination-next:not(.ant-pagination-disabled)")
                    if next_button.count() > 0 and next_button.is_visible():
                        next_button.click()
                        page_index += 1
                        page.wait_for_timeout(1000)
                    else:
                        break # Hết trang

                except Exception:
                    break            

            # Lọc dữ liệu rác (những dòng không có thứ/tiết)
            cleaned_data = []
            for item in final_data:
                has_day = item["Thứ"] not in ["N/A", "", None]
                has_period = item["Tiết học"] not in ["N/A", "", None]
                if has_day and has_period:
                    cleaned_data.append(item)
            
            final_data = cleaned_data

            if not final_data:
                print(Fore.RED + f" Không tìm thấy lớp học phần nào cho mã {course_code}. Đã bỏ qua.")
                continue
            
            all_data["courses"][course_code] = final_data
            
    except Exception as main_err:
        print(Fore.RED + f"\n Lỗi trong quá trình xử lý: {main_err}")
    
    # -----------------------------------------------------------
    # BƯỚC 4: XUẤT DỮ LIỆU RA EXCEL
    # -----------------------------------------------------------
    finally:
        export_data = []
        if "courses" in all_data:
            for code, data in all_data["courses"].items():
                export_data.extend(data)

        if export_data:
            output_folder = "KetQua_Excel"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            df = pd.DataFrame(export_data)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"{timestamp}_dulieu_hocphan.xlsx"
            full_path = os.path.join(output_folder, filename)

            df.to_excel(full_path, index=False)
            print(Fore.GREEN + f" Đã xuất dữ liệu ra file: {full_path}")
        else:
            print(Fore.RED + "\n Không tìm thấy dữ liệu nào để xuất hoặc có lỗi xảy ra.")

        if browser: browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)