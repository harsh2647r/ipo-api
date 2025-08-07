# app.py
import asyncio
from flask import Flask, jsonify, render_template_string
from playwright.async_api import async_playwright

app = Flask(__name__)

URL = "https://www.chittorgarh.com/report/ipo-subscription-status-live-bidding-data-bse-nse/21/?year=2025"

async def fetch_ipo_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = await context.new_page()
        try:
            await page.goto(URL, wait_until="load", timeout=15000)
            await page.wait_for_selector("#report_table tbody tr", timeout=15000)
        except Exception as e:
            print(f"Error: {e}")
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

@app.route("/api/ipo")
def ipo_api():
    ipo_data = asyncio.run(fetch_ipo_data())
    return jsonify(ipo_data)

@app.route("/")
def home():
    page_html = """
<!DOCTYPE html>
<html>
<head>
    <title>IPO Subscription Data</title>
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
            max-width: 1000px;
            margin: 20px auto;
            font-family: Arial, sans-serif;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
        }
        tr:nth-child(even) {background-color: #f2f2f2;}
        tr:hover {background-color: #ddd;}
        #last-updated {
            font-size: 14px;
            color: #555;
            text-align: center;
            margin-bottom: 10px;
        }
        .share-btn {
            padding: 6px 12px;
            font-size: 14px;
            background-color: #2196F3;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 4px;
        }
    </style>
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
</head>
<body>
    <h1 style="text-align:center;">Live IPO Subscription Data</h1>
    <button onclick="loadData()">Refresh Data</button>
    <div id="last-updated"></div>
    <div id="table-container"></div>

    <script>
        let ipoData = [];

        const headers = [
            { key: 'company_name', label: 'Company Name' },
            { key: 'close_date', label: 'Close Date' },
            { key: 'size_rs_cr', label: 'Size (Rs Cr)' },
            { key: 'QIB_x', label: 'QIB (x)' },
            { key: 'sNII_x', label: 'sNII (x)' },
            { key: 'bNII_x', label: 'bNII (x)' },
            { key: 'NII_x', label: 'NII (x)' },
            { key: 'Retail_x', label: 'Retail (x)' },
            { key: 'Employee_x', label: 'Employee (x)' },
            { key: 'Others', label: 'Others' },
            { key: 'Share', label: 'Share' }
        ];

        function renderTable() {
            const container = document.getElementById('table-container');
            let html = '<table><thead><tr>';
            headers.forEach(h => {
                html += `<th>${h.label}</th>`;
            });
            html += '</tr></thead><tbody>';

            ipoData.forEach((item, index) => {
                html += `<tr id="ipo-row-${index}">`;
                headers.forEach(h => {
                    if (h.key === 'Share') {
                        html += `<td><button class="share-btn" onclick="shareIPO(${index})">📤 Share</button></td>`;
                    } else {
                        html += `<td>${item[h.key] || ''}</td>`;
                    }
                });
                html += '</tr>';
            });

            html += '</tbody></table>';
            container.innerHTML = html;
        }

        async function loadData() {
            const container = document.getElementById('table-container');
            const lastUpdatedDiv = document.getElementById('last-updated');
            container.innerHTML = "<p style='text-align:center;'>Loading...</p>";
            try {
                const response = await fetch('/api/ipo?cachebuster=' + new Date().getTime());
                ipoData = await response.json();
                renderTable();
                lastUpdatedDiv.textContent = "Last Updated On: " + new Date().toLocaleString();
            } catch (err) {
                container.innerHTML = "<p style='color:red; text-align:center;'>Error: " + err + "</p>";
                lastUpdatedDiv.textContent = "";
            }
        }

        async function shareIPO(index) {
            const data = ipoData[index];
            const displayDiv = document.createElement('div');
            displayDiv.style.position = 'fixed';
            displayDiv.style.left = '-9999px';
            displayDiv.style.background = '#fff';
            displayDiv.style.border = '1px solid #ccc';
            displayDiv.style.padding = '16px';
            displayDiv.style.fontFamily = 'Arial';
            displayDiv.style.lineHeight = '1.6';
            displayDiv.style.width = '300px';

            headers.slice(0, -1).forEach(h => {
                const line = document.createElement('div');
                line.innerHTML = `<strong>${h.label}:</strong> ${data[h.key] || ''}`;
                displayDiv.appendChild(line);
            });

            const footer = document.createElement('div');
            footer.textContent = "Shared from: Live IPO Subscription Data";
            footer.style.fontSize = '12px';
            footer.style.textAlign = 'center';
            footer.style.color = '#777';
            footer.style.marginTop = '12px';
            displayDiv.appendChild(footer);

            document.body.appendChild(displayDiv);

            const canvas = await html2canvas(displayDiv);
            canvas.toBlob(async (blob) => {
                try {
                    await navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]);
                    alert("Image copied to clipboard!");
                } catch (err) {
                    alert("Copy failed. Try in Chrome/Edge desktop.");
                    console.error(err);
                }
            });

            document.body.removeChild(displayDiv);
        }

        window.onload = () => {
            loadData();
            setInterval(loadData, 60000);
        };
    </script>
</body>
</html>
"""
    return render_template_string(page_html)

if __name__ == "__main__":
    app.run(debug=True)
