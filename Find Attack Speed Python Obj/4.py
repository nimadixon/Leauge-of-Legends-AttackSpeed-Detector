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
    lastAttackTime = time.time() * 1000  # زمان اولیه حمله به میلی‌ثانیه

    print("برنامه اجرا شد. برای خروج، کلید NUMPAD9 را بزنید.")
    
    while True:

        if GetAsyncKeyState(win32con.VK_NUMPAD9) & 0x8000:  # بررسی فشار دادن کلید NUMPAD9 برای خروج
            print("خروج از برنامه...")
            break

        if GetAsyncKeyState(win32con.VK_SPACE) & 0x8000:  # بررسی فشار دادن کلید Space
            print("دکمه Space فشار داده شد.")
            
            # گرفتن عدد از تصویر هر بار که Space فشار داده می‌شود
            number, img = get_number_from_image()
            if number:
                print(f"عدد شناسایی شده: {number}")

            # تبدیل عدد به attackPerSecond
            try:
                attackPerSecond = float(number)  # عدد شناسایی شده به حمله در ثانیه
                coolDownTime = 1000 / attackPerSecond  # محاسبه زمان Cooldown بر اساس attackPerSecond
                print(f"زمان Cooldown محاسبه شد: {coolDownTime} میلی‌ثانیه")
            except ValueError:
                print("عدد شناسایی شده معتبر نیست.")
                continue

            # حلقه‌ای برای کلیک چپ مداوم
            while GetAsyncKeyState(win32con.VK_SPACE) & 0x8000:  # تا زمانی که دکمه Space نگه داشته شده باشد
                # انجام اولین کلیک چپ
                click_left()
                print("کلیک چپ انجام شد.")

                # تاخیر 0.206 ثانیه برای انجام کلیک راست
                sleep(0.206)

                # انجام کلیک راست
                click_right()
                print("کلیک راست انجام شد.")
                
                # صبر کردن به مدت Cooldown (تأخیر بین شلیک‌ها)
                sleep(coolDownTime / 1000)  # صبر به مدت Cooldown در ثانیه (از میلی‌ثانیه به ثانیه تبدیل می‌شود)
                

            print("دکمه Space رها شده است. حلقه متوقف شد.")
        
        # تاخیر بسیار کوتاه برای جلوگیری از بیش از حد پردازش در حلقه
        sleep(0.01)

    cv2.destroyAllWindows()  # بستن پنجره OpenCV

if __name__ == "__main__":
    main()
