from playwright.sync_api import sync_playwright
import os
import smtplib
from email.message import EmailMessage

def send_email(file_path):
    sender_email = "daystartest1@gmail.com"
    receiver_email = "daystartest1@gmail.com"
    password = "nvrs svhj oxuw bvmc"

    msg = EmailMessage()
    msg['Subject'] = 'Amazon Shipping Label'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content("Please find attached today's Amazon shipping label.")

    with open(file_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(file_path))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, password)
        smtp.send_message(msg)

    print("✅ Email sent successfully.")

def download_sent_label():
    os.makedirs("labels", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            storage_state="cookies/amazon_cookies.json",
            accept_downloads=True
        )
        page = context.new_page()

        def clear_all_blockers():
            page.evaluate("""
                const overlay = document.querySelector('.react-joyride__overlay');
                if (overlay) overlay.parentElement.remove();

                const portal = document.querySelector('#react-joyride-portal');
                if (portal) portal.remove();

                const modals = document.querySelectorAll('[class*="joyride"], [class*="popup"], [id*="popup"]');
                modals.forEach(m => m.remove());

                const onboardingModal = document.querySelector('.sellerOnboardingPopup');
                if (onboardingModal) onboardingModal.remove();
            """)

        page.goto("https://sellercentral.amazon.in/orders-v3")
        print("📦 Navigating to Easy Ship > Sent > Ship Today")
        page.wait_for_timeout(8000)

        try:
            if page.locator("kat-modal.sellerOnboardingPopup").is_visible():
                print("🔕 Closing onboarding popup...")
                try:
                    page.click("kat-modal.sellerOnboardingPopup button[aria-label='Close']", timeout=3000)
                    page.wait_for_timeout(1000)
                except:
                    clear_all_blockers()
                    page.wait_for_timeout(1000)
            else:
                clear_all_blockers()

            page.click("text='Sent'", timeout=8000)
            page.wait_for_timeout(3000)
            clear_all_blockers()

            page.locator("label[data-test-id='option-value-today'] input[type='radio']").click(force=True)
            page.wait_for_timeout(2000)

            page.wait_for_selector("table input[type='checkbox']", timeout=10000)
            page.locator("table input[type='checkbox']").first.click(force=True)
            print("☑️ Master checkbox selected.")

            with page.expect_navigation(timeout=20000):
                page.click("text='Print shipping label(s)'", timeout=8000)

            print("⏳ Waiting for label processing page to load...")

            found = False
            for attempt in range(6):  # Up to 2 minutes (6×20s)
                print(f"🔁 Checking for 'Download Shipping Labels' (try {attempt + 1}/6)...")

                rows = page.locator("table tr:has-text('Done')")
                if rows.count() > 0:
                    print("✅ Found 'Done' status. Downloading now...")

                    with page.expect_download() as download_info:
                        page.click("text='Download Shipping Labels'", timeout=5000)

                    download = download_info.value
                    file_path = os.path.join("labels", download.suggested_filename)
                    download.save_as(file_path)
                    print(f"✅ Label downloaded: {file_path}")

                    send_email(file_path)
                    found = True
                    break

                print("🔄 Refreshing...")
                page.click("input[name='refresh']", force=True)
                page.wait_for_timeout(20000)

            if not found:
                print("❌ Download link did not appear in 2 minutes.")

        except Exception as e:
            print("❌ Error:", e)

        browser.close()

if __name__ == "__main__":
    download_sent_label()
