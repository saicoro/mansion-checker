import os
import requests
from playwright.sync_api import sync_playwright

# --- 設定エリア ---
# GitHub Secretsから取得
LINE_TOKEN = os.getenv("LINE_TOKEN") 
TARGET_URL = "https://www.31sumai.com/attend/X2571/"
# ----------------

def send_line_notification(message):
    """LINEに通知を送る関数"""
    if not LINE_TOKEN:
        print("エラー: LINE_TOKENが設定されていません。")
        return
    
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"message": message}
    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            print("LINE通知を送信しました。")
        else:
            print(f"LINE通知失敗: {response.status_code}")
    except Exception as e:
        print(f"通知エラー: {e}")

def monitor_reservation():
    with sync_playwright() as p:
        # サーバー実行用に headless=True
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"チェック開始: {TARGET_URL}")
        try:
            # ページへ移動（ネットワークが落ち着くまで待機）
            page.goto(TARGET_URL, wait_until="networkidle")
            
            # JavaScriptの描画（カレンダー等）を待つために5秒待機
            page.wait_for_timeout(5000)

            # ページ全体のテキストを取得
            content = page.content()

            # 【重要】判定ロジック：「○」がある場合のみ通知
            if "○" in content:
                msg = f"\n【予約空きあり！】\n三井不動産レジデンシャルのページに「○」が出ました！\nすぐ確認してください！\n{TARGET_URL}"
                print("「○」を発見しました！通知を送ります。")
                send_line_notification(msg)
            else:
                # 「○」がない場合はログを出すだけで、LINEは送りません
                print("空き（○）は見つかりませんでした。")

        except Exception as e:
            print(f"実行エラー: {e}")
        
        browser.close()

if __name__ == "__main__":
    monitor_reservation()
