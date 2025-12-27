import re
import sys
import time
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright
from colorama import Fore, Style, init
import pwinput

try:
    import pygetwindow as gw
except ImportError:
    print("Vui lòng cài đặt thư viện: pip install pygetwindow")
    sys.exit(1)

init(autoreset=True)

BANNER = r"""
┌───────────────────────────────────────────────────────────────┐
│                   Huaniverse Timetable Tool                   │
└───────────────────────────────────────────────────────────────┘
"""

# ==========================================
# UI & Formatting Utilities
# ==========================================
def rgb_text(r, g, b, text):
    return f"\033[1;38;2;{r};{g};{b}m{text}"

def print_gradient_banner(text):
    lines = [line for line in text.split('\n') if line]
    if not lines: return

    max_width = max(len(line) for line in lines)
    start_color = (0, 139, 255)
    end_color = (95, 255, 236)

    for line in lines:
        colored_line = ""
        for i, char in enumerate(line):
            ratio = i / max_width if max_width > 0 else 0
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            colored_line += rgb_text(r, g, b, char)
        print(Style.BRIGHT + colored_line + Style.RESET_ALL)

# ==========================================
# Input Validators
# ==========================================
def validate_academic_year(year: str) -> bool:
    return bool(re.match(r"^\d{4}-\d{4}$", year))

def validate_semester(sem: str) -> bool:
    return sem in ["1", "2", "3"]

def validate_course_code(code: str) -> bool:
    return bool(re.match(r"^[A-Z]{2}\d{3}E?$", code))

# ==========================================
# Window Management
# ==========================================
def minimize_browser_window():
    """Attempts to find and minimize the browser window to reduce visual clutter."""
    try:
        time.sleep(1) 
        windows = []
        # Check for common browser window titles
        for title in ['Chromium', 'Chrome', 'Google Chrome']:
            windows = gw.getWindowsWithTitle(title)
            if windows: break
        
        if windows and not windows[0].isMinimized:
            windows[0].minimize()
    except Exception:
        pass

# ==========================================
# Main Execution
# ==========================================
def run(playwright):
    print_gradient_banner(BANNER)

    all_data = {"courses": {}}
    academic_year = ""
    semester = ""

    # 1. Collect User Inputs
    print(Fore.GREEN + "                            ĐĂNG NHẬP")
    username = input(Fore.CYAN + Style.BRIGHT + " Nhập MSSV: " + Fore.WHITE)
    password = pwinput.pwinput(prompt= Fore.CYAN + " Nhập mật khẩu: ", mask= "•")
    print_gradient_banner("─────────────────────────────────────────────────────────────────")

    while True:
        academic_year = input(Fore.MAGENTA + " Nhập năm học (ví dụ 2025-2026): " + Fore.WHITE)
        if validate_academic_year(academic_year): break
        print(Fore.RED + " Năm học không hợp lệ.")

    while True:
        semester = input(Fore.MAGENTA + " Nhập học kỳ (1,2,3): " + Fore.WHITE)
        if validate_semester(semester): break
        print(Fore.RED + " Học kỳ phải là số 1, 2 hoặc 3")

    while True:
        course_input = input(Fore.MAGENTA + " Nhập các mã học phần (cách nhau bằng dấu phẩy): " + Fore.WHITE)
        course_codes = [code.strip().upper() for code in course_input.split(",") if code.strip()]
        if all(validate_course_code(code) for code in course_codes): break
        print(Fore.RED + " Mã học phần không hợp lệ")

    print_gradient_banner("─────────────────────────────────────────────────────────────────")
    print(Fore.YELLOW + " Đang khởi động trình duyệt...", end="\r")
    
    # 2. Initialize Browser
    browser = playwright.chromium.launch(headless=False)
    # Fixed viewport prevents responsive layout issues when minimized
    context = browser.new_context(viewport={'width': 1366, 'height': 768})
    page = context.new_page()

    minimize_browser_window()

    print(Fore.YELLOW + " Đang đăng nhập..." +" " *20, end="\r")
    
    # 3. Authentication Flow
    try:
        page.goto("https://htql.ctu.edu.vn/htql/login.php")
        page.fill("#usernameUserInput", username) 
        page.fill("#password", password)
        page.click("#sign-in-button")
        
        try:
            page.wait_for_url("**/htql/sinhvien/hindex.php", timeout=5000)
        except:
            pass 
            
    except Exception as e:
        print(Fore.RED + f"\n Lỗi đăng nhập hoặc kết nối: {e}")
        browser.close()
        return

    print(Fore.GREEN + " Đăng nhập thành công", end = " ")

    # 4. Navigate to Course Registration Page
    try:
        page.goto("https://dkmh.ctu.edu.vn/htql/sinhvien/hindex.php")
        print(Fore.GREEN + "--> dkmh.ctu.edu.vn", end = " ")
        
        # Handle fallback if the direct link image isn't available
        link_dk = page.locator("img[onclick='gotoDKindex()']")
        if link_dk.is_visible():
            link_dk.click()
        else:
            page.goto("https://dkmhfe.ctu.edu.vn/dangkyhocphan/sinhvien/quydinhdangky")
        
        page.wait_for_url("**/dangkyhocphan/sinhvien/quydinhdangky", timeout=10000)
        print(Fore.GREEN + "--> dkmhfe.ctu.edu.vn")
        
        page.click("text=Danh mục học phần")
        page.wait_for_selector("#rc_select_0", state="visible")

        all_data["academic_year"] = academic_year
        all_data["semester"] = semester

        page.fill("#rc_select_0", academic_year)
        page.keyboard.press("Tab")
        page.keyboard.type(semester)

        # 5. Data Extraction Loop
        for course_code in course_codes:
            print(Fore.YELLOW + f" Đang lấy dữ liệu học phần {course_code}..." + " "*20,end = "\r")

            # Reset search box
            page.click("#rc_select_2") 
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            
            # Search for specific course
            page.fill("#rc_select_2", course_code)
            page.click("span[aria-label='search']")
            page.wait_for_timeout(1500) 

            # Extract Course Name
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

            final_data = []
            current_group = None
            page_index = 1

            # Handle Pagination & Table Parsing
            while True:
                try:
                    page.wait_for_selector("tbody.ant-table-tbody tr", timeout=3000)
                    rows = page.locator("tbody.ant-table-tbody tr")
                    count = rows.count()

                    if count == 0: break

                    raw_data = []
                    for i in range(count):
                        cells = rows.nth(i).locator("td")
                        row_data = [cells.nth(j).inner_text().strip() for j in range(cells.count())]
                        if row_data: raw_data.append(row_data)

                    # Normalize data rows (fix merged/empty cells)
                    normalized_data = []
                    for row in raw_data:
                        if len(row) == 25: 
                            row.insert(0, "")
                            row.insert(0, "")
                        normalized_data.append(row)

                    for row in normalized_data:
                        # Group merging logic
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
                            "Tiết học": re.sub(r'-', '', get_col(6)),
                            "Phòng": get_col(7),
                            "Sĩ số": f"{get_col(5)}/{get_col(4)}" if get_col(5) != "N/A" else "N/A",
                            "Giảng viên": row[-1] if len(row) > 0 else "N/A"
                        })

                    # Check for "Next" button
                    next_button = page.locator("li.ant-pagination-next:not(.ant-pagination-disabled)")
                    if next_button.count() > 0 and next_button.is_visible():
                        next_button.click()
                        page_index += 1
                        page.wait_for_timeout(1000)
                    else:
                        break

                except Exception:
                    break            

            # 6. Data Cleaning
            # Filter out rows that lack schedule information (Day/Period)
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
    
    # 7. Export Results
    finally:
        export_data = []
        if "courses" in all_data:
            for code, data in all_data["courses"].items():
                export_data.extend(data)

        if export_data:
            df = pd.DataFrame(export_data)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"{timestamp}_dulieu_hocphan.xlsx"
            df.to_excel(filename, index=False)
            print(Fore.GREEN + f" Đã xuất dữ liệu ra file: {filename}")
        else:
            print(Fore.RED + "\n Không tìm thấy dữ liệu nào để xuất hoặc có lỗi xảy ra.")

        browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)