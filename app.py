import asyncio
from flask import Flask, jsonify
from playwright.async_api import async_playwright
from datetime import datetime

app = Flask(__name__)

IPO_URL = "https://www.chittorgarh.com/report/ipo-subscription-status-live-bidding-data-bse-nse/21/?year=2025"

async def get_ipo_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(IPO_URL, timeout=60000)

        await page.wait_for_selector("table.table.table-sm")

        tables = await page.query_selector_all("table.table.table-sm")

        ipo_data = []
        for table in tables:
            title_elem = await table.query_selector("thead tr th")
            if not title_elem:
                continue
            title = (await title_elem.inner_text()).strip()

            rows = await table.query_selector_all("tbody tr")
            row_data = []
            for row in rows:
                cells = await row.query_selector_all("td")
                cell_values = [await cell.inner_text() for cell in cells]
                row_data.append(cell_values)

            ipo_data.append({
                "ipo_name": title,
                "data": row_data
            })

        await browser.close()
        return ipo_data

@app.route("/")
def home():
    return "IPO Data API is live"

@app.route("/ipo-data")
def ipo_data():
    data = asyncio.run(get_ipo_data())
    return jsonify({
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ipos": data
    })

if __name__ == "__main__":
    app.run(debug=True)
