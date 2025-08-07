import os
from flask import Flask, jsonify
from playwright.async_api import async_playwright
from asgiref.sync import async_to_sync

app = Flask(__name__)

URL = "https://www.chittorgarh.com/report/ipo-subscription-status-live-bidding-data-bse-nse/21/?year=2025"

async def fetch_ipo_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto(URL, wait_until="load", timeout=15000)
            await page.wait_for_selector("#report_table tbody tr", timeout=15000)
        except Exception as e:
            print(f"Error loading page: {e}")
            await browser.close()
            return []

        data = await page.evaluate("""() => {
            const rows = document.querySelectorAll("#report_table tbody tr");
            return Array.from(rows).map(row => {
                const cols = row.querySelectorAll("td");
                return {
                    company_name: cols[0]?.innerText.trim(),
                    close_date: cols[1]?.innerText.trim(),
                    size_rs_cr: cols[2]?.innerText.trim(),
                    QIB_x: cols[3]?.innerText.trim(),
                    sNII_x: cols[4]?.innerText.trim(),
                    bNII_x: cols[5]?.innerText.trim(),
                    NII_x: cols[6]?.innerText.trim(),
                    Retail_x: cols[7]?.innerText.trim(),
                    Employee_x: cols[8]?.innerText.trim(),
                    Others: cols[9]?.innerText.trim(),
                };
            });
        }""")

        await browser.close()
        return data

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the IPO API. Access /api/ipo for IPO data."})

@app.route("/api/ipo")
def ipo_api():
    data = async_to_sync(fetch_ipo_data)()
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
