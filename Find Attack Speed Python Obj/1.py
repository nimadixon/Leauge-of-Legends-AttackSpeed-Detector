import cv2
import numpy as np
import dxcam
import pytesseract
from win32api import GetAsyncKeyState
import win32con
import ctypes
import time
from time import sleep

# تنظیم مسیر Tesseract (مطمئن شو که نصب شده)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# تنظیم منطقه‌ی اسکن برابر با رزولوشن مانیتور
region = (246, 844, 280, 862)  # رزولوشن تو

scr = dxcam.create(output_color="BGR")  # گرفتن تصویر با رنگ مناسب OpenCV

def process_image(image):
    """پردازش تصویر برای خواندن عدد"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # تبدیل به سیاه‌وسفید
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)  # باینری کردن تصویر
    return binary

def get_number_from_image():
    """گرفتن عدد از تصویر و پردازش با OCR"""
    pic = scr.grab(region=region)  # گرفتن اسکرین‌شات از منطقه مشخص‌شده

    if pic is None:
        return None, None

    image_np = np.array(pic)  # تبدیل PIL به numpy برای OpenCV
    processed_img = process_image(image_np)

    # استفاده از OCR برای استخراج متن (فقط اعداد)
    number = pytesseract.image_to_string(processed_img, config="--psm 6 digits")
    
    return number.strip(), processed_img

def click_left():
    """شبیه‌سازی کلیک چپ موس با استفاده از ctypes"""
    ctypes.windll.user32.mouse_event(0x02, 0, 0, 0, 0)  # کلیک چپ پایین
    ctypes.windll.user32.mouse_event(0x04, 0, 0, 0, 0)  # کلیک چپ بالا

def click_right():
    """شبیه‌سازی کلیک راست موس با استفاده از ctypes"""
    ctypes.windll.user32.mouse_event(0x08, 0, 0, 0, 0)  # کلیک راست پایین
    ctypes.windll.user32.mouse_event(0x10, 0, 0, 0, 0)  # کلیک راست بالا

def main():
    print("برنامه اجرا شد. برای خروج، کلید NUMPAD9 را بزنید.")
    
    while True:
        if GetAsyncKeyState(win32con.VK_NUMPAD9):  # کلید 9 برای خروج
            print("خروج از برنامه...")
            break
        
        number, img = get_number_from_image()
        if number:
            print(f"عدد شناسایی شده: {number}")
        
        # بررسی فشار دادن دکمه ALT
        if GetAsyncKeyState(win32con.VK_MENU):  # بررسی فشار دادن دکمه ALT (که معمولا به صورت VK_MENU شناخته می‌شود)
            print("دکمه ALT فشار داده شد.")
            
            # انجام اولین کلیک چپ
            click_left()
            print("کلیک چپ انجام شد.")
            
            try:
                # تبدیل عدد به مدت زمان float
                wait_time = float(number)  # استفاده از float به‌طور مستقیم
                print(f"صبر کردن به مدت {wait_time} ثانیه...")
                sleep(wait_time)  # صبر به مدت عدد شناسایی شده (به صورت float)
                
                # انجام کلیک راست بعد از گذشت زمان مشخص
                click_right()
                print("کلیک راست بعد از گذشت زمان.")
            except ValueError:
                print("عدد شناسایی شده معتبر نیست.")
            
            time.sleep(0.5)  # تاخیر برای جلوگیری از تکرار سریع

        sleep(0.5)  # هر نیم‌ثانیه یک‌بار بررسی کند

    cv2.destroyAllWindows()  # بستن پنجره OpenCV

main()
