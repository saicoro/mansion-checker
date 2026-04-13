import os
import requests
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

# --- 設定（通知先） ---
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# --- 監視対象リスト ---
TARGET_SITES = [
    {"name": "パークコート麻布十番東京ザタワー", "url": "https://www.31sumai.com/attend/X2571/"},
    {"name": "パークコートお茶の水ザタワー", "url": "https://www.31sumai.com/attend/X2125/"},
]

def send_notifications(site_name, site_url):
    """発見時にDiscordとメールで一斉通知する"""
    message = f"【予約空き発見！】\n物件：{site_name}\n\n今すぐ予約：\n{site_url}"
    
    # 1. Discord通知（原因調査用ログ追加版）
    if DISCORD_URL:
        try:
            main_content = {"content": f"@everyone {message}"}
            response = requests.post(DISCORD_URL, json=main_content, timeout=10)
            print(f"Discord送信ステータス: {response.status_code}") # ここが 200 なら成功
            if response.status_code != 200:
                print(f"Discordエラー詳細: {response.text}")
        except Exception as e:
            print(f"Discord接続エラー: {e}")

    # 2. メール通知（複数アドレス対応）
    if EMAIL_USER and EMAIL_PASS and EMAIL_RECEIVER:
        receivers = [r.strip() for r in EMAIL_RECEIVER.split(",")]
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as s:
                s.login(EMAIL_USER, EMAIL_PASS)
                for addr in receivers:
                    msg = MIMEText(message)
                    msg["Subject"] = f"【至急】{site_name} に予約空き（○）を発見！"
                    msg["From"] = EMAIL_USER
                    msg["To"] = addr
                    s.send_message(msg)
                    print(f"メール送信成功: {addr}")
        except Exception as e:
            print(f"メール送信エラー: {e}")

def check_site(page, site):
    """個別の物件をチェックする"""
    name = site["name"]
    url = site["url"]
    try:
        print(f"チェック中: {name} ({url})")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        page.wait_for_timeout(5000)
        
        has_circle = (page.locator(".status_3").count() > 0) or ("○" in page.content())
        
        if has_circle:
            print(f"【発見！】{name}")
            send_notifications(name, url)
        else:
            print(f"空きなし: {name}")
    except Exception as e:
        print(f"エラー発生 ({name}): {e}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        for site in TARGET_SITES:
            check_site(page, site)
        browser.close()

if __name__ == "__main__":
    main()
