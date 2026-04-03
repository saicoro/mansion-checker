import os
import requests
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

# --- 設定（GitHub Secretsから自動的に読み込まれます） ---
LINE_TOKEN = os.getenv("LINE_TOKEN")
EMAIL_USER = os.getenv("EMAIL_USER")      # 送信元のGmailアドレス
EMAIL_PASS = os.getenv("EMAIL_PASS")      # Googleで発行した16桁のアプリパスワード
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER") # 通知を受け取りたいメールアドレス
TARGET_URL = "https://www.31sumai.com/attend/X2571/"

def send_notifications(message):
    """LINEとメールの両方に通知を送る関数"""
    
    # 1. LINE通知の送信
    if LINE_TOKEN:
        try:
            url = "https://notify-api.line.me/api/notify"
            headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
            payload = {"message": message}
            requests.post(url, headers=headers, data=payload)
            print("LINE通知を送信しました。")
        except Exception as e:
            print(f"LINE送信エラー: {e}")

    # 2. メール通知の送信（Gmailサーバー経由）
    if EMAIL_USER and EMAIL_PASS and EMAIL_RECEIVER:
        msg = MIMEText(message)
        msg["Subject"] = "【至急】マンション予約に空き（○）が出ました"
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_RECEIVER

        try:
            # GmailのSMTPサーバー（ポート465）を使用
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_USER, EMAIL_PASS)
                server.send_message(msg)
            print("メール通知を送信しました。")
        except Exception as e:
            print(f"メール送信エラー: {e}")

def monitor_reservation():
    """サイトを巡回してチェックするメイン関数"""
    with sync_playwright() as p:
        # ブラウザの起動
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print(f"チェック開始: {TARGET_URL}")
            # ページ読み込み（ネットワークが落ち着くまで待機）
            page.goto(TARGET_URL, wait_until="networkidle")
            # 念のため5秒待機（動的な読み込み対策）
            page.wait_for_timeout(5000)
            
            content = page.content()

            # 「○」という文字が含まれているか判定
            if "○" in content:
                print("【発見】予約の空き（○）があります！")
                msg = f"\n予約空き（○）を発見しました！\nすぐに確認してください：\n{TARGET_URL}"
                send_notifications(msg)
            else:
                print("空き（○）は見つかりませんでした。")
                
        except Exception as e:
            print(f"モニタリング中にエラーが発生しました: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    monitor_reservation()
