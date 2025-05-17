from playwright.sync_api import sync_playwright

def save_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://sellercentral.amazon.in/")
        print("🔓 Please log in manually in the browser window...")
        input("✅ Press Enter here after successful login.")
        context.storage_state(path="cookies/amazon_cookies.json")
        print("✅ Login cookies saved.")
        browser.close()

if __name__ == "__main__":
    save_cookies()
