from playwright.sync_api import sync_playwright

def take_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # 好きな天気サイトに変更OK！
        page.goto("https://tenki.jp/forecast/3/16/")
        page.screenshot(path="weather.png", full_page=True)
        browser.close()

if __name__ == "__main__":
    take_screenshot()