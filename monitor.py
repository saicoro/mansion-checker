import os
import requests
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

# --- 設定 ---
LINE_TOKEN = os.getenv("LINE_TOKEN")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
TARGET_URL = "https://www.31sumai.com/attend/X2571/"

def send_notifications(message):
    # LINE通知
    if LINE_TOKEN:
        try:
            requests.post("https://notify-api.line.me/api/notify", 
                          headers={"Authorization": f"Bearer {LINE_TOKEN}"}, 
                          data={"message": message}, timeout=10)
        except: pass
    # メール通知
    if EMAIL_USER and EMAIL_PASS:
        msg = MIMEText(message); msg["Subject"] = "【至急】予約空き（○）を発見！"; msg["From"] = EMAIL_USER; msg["To"] = EMAIL_RECEIVER
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as s:
                s.login(EMAIL_USER, EMAIL_PASS); s.send_message(msg)
        except: pass

def monitor():
    with sync_playwright() as p:
        # 月島監視から拝借した「軽量化オプション」
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        try:
            # 2段構えの待機（月島流）
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            try: page.wait_for_load_state("networkidle", timeout=10000)
            except: pass
            page.wait_for_timeout(5000) # ダメ押しの5秒
            
            # クラス名と文字の両方で「○」を逃さない
            has_circle_class = page.locator(".status_3").count() > 0
            has_circle_text = "○" in page.content()
            
            if has_circle_class or has_circle_text:
                msg = f"\n予約空き（○）を発見！\n即座に確保してください：\n{TARGET_URL}"
                send_notifications(msg)
                print("【発見】通知を送信しました。")
            else:
                print("空きなし。")
        finally:
            browser.close()

if __name__ == "__main__":
    monitor()
