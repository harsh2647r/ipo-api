import asyncio
from playwright.async_api import async_playwright
import json

URL = "https://www.chittorgarh.com/report/ipo-subscription-status-live-bidding-data-bse-nse/21/?year=2025"

async def fetch_ipo_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        page = await context.new_page()
        try:
            await page.goto(URL, wait_until="load", timeout=15000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            await browser.close()
            return []

        # Wait for the table rows to load
        try:
            await page.wait_for_selector("#report_table tbody tr", timeout=15000)
        except Exception as e:
            print(f"Table rows not found or took too long to load: {e}")
            await browser.close()
            return []

        # Extract all columns from each row
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

def main():
    ipo_data = asyncio.run(fetch_ipo_data())
    if ipo_data:
        print(json.dumps(ipo_data, indent=2))
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()
