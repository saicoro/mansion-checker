import requests
from playwright.sync_api import sync_playwright

# --- 設定エリア ---
LINE_TOKEN = "m2l+a2223726047@m2l.codyltech.com"
TARGET_URL = "https://www.31sumai.com/attend/X2571/"
# ----------------

def send_line_notification(message):
    """LINEに通知を送る関数"""
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"message": message}
    requests.post(url, headers=headers, data=payload)

def monitor_reservation():
    with sync_playwright() as p:
        # ブラウザ起動（サーバーで動かす際はheadless=Trueにします）
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"チェック開始: {TARGET_URL}")
        try:
            page.goto(TARGET_URL, wait_until="networkidle")
            
            # カレンダーの読み込み待ち（念のため5秒待機）
            page.wait_for_timeout(5000)

            # ページ全体のテキストを取得
            content = page.content()

            # 判定ロジック
            if "○" in content:
                msg = f"\n【予約空き発生！】\n三井不動産レジデンシャルのページに「○」が表示されました！\nすぐ確認してください！\n{TARGET_URL}"
                print(msg)
                send_line_notification(msg)
            else:
                print("まだ「○」は見当たりません。")

        except Exception as e:
            print(f"エラー発生: {e}")
        
        browser.close()

if __name__ == "__main__":
    monitor_reservation()