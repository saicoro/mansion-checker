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

# 解析したコードから拝借した「本物のブラウザ」に見せるための設定
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

def send_notifications(message):
    if LINE_TOKEN:
        try:
            url = "https://notify-api.line.me/api/notify"
            headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
            payload = {"message": message}
            requests.post(url, headers=headers, data=payload, timeout=10)
        except Exception as e:
            print(f"LINE Error: {e}")

    if EMAIL_USER and EMAIL_PASS and EMAIL_RECEIVER:
        msg = MIMEText(message)
        msg["Subject"] = "【至急】マンション予約に空き（○）を発見！"
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_RECEIVER
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
                server.login(EMAIL_USER, EMAIL_PASS)
                server.send_message(msg)
        except Exception as e:
            print(f"Mail Error: {e}")

def monitor():
    with sync_playwright() as p:
        # User-Agentを偽装してブラウザを起動
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        
        try:
            # タイムアウトを30秒に設定（解析コードの知恵）
            page.set_default_timeout(30000)
            print(f"チェック中: {TARGET_URL}")
            
            page.goto(TARGET_URL, wait_until="networkidle")
            # カレンダー描画のために少し待つ
            page.wait_for_timeout(5000)
            
            if "○" in page.content():
                print("発見！")
                msg = f"\n予約空き（○）を発見しました！\nすぐに確認してください：\n{TARGET_URL}"
                send_notifications(msg)
            else:
                print("空きなし。")
                
        except Exception as e:
            print(f"Error during monitoring: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    monitor()
