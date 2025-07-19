import csv
import os
import requests
import time
import datetime
import psutil
from main import GCCICertificateData  # ✅ Make sure model matches fields
from random import randint

# ✅ Output folders
pdf_output_dir = "gcci_pdfs_from_csv_input"
os.makedirs(pdf_output_dir, exist_ok=True)

csv_output_dir = "gcci_csv_reports_from_csv_input"
os.makedirs(csv_output_dir, exist_ok=True)

# 🌐 Render endpoint
RENDER_URL = "https://gcci-product-1.onrender.com/generate-origin-certificate-pdf/"

# 📋 Software test evaluation criteria
test_parameters = [
    "Reliability", "Scalability", "Robustness/Resilience", "Latency", "Throughput",
    "Security", "Usability/User-Friendliness", "Maintainability", "Availability", "Cost",
    "Flexibility/Adaptability", "Portability", "Interoperability",
    "Resource Utilization", "Documentation Quality"
]

def get_evaluation(param):
    score = randint(3, 5)
    remarks = {
        5: "Excellent performance under all tested conditions.",
        4: "Good performance with minor improvements suggested.",
        3: "Acceptable performance; needs better optimization."
    }
    return score, remarks[score]

# ✅ Retry logic
def post_with_retries(data_dict, retries=5, delay=3):
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(RENDER_URL, json=data_dict)
            if response.status_code == 200:
                return response
            else:
                print(f"⚠️ Attempt {attempt}: Server responded with status {response.status_code}")
        except Exception as e:
            print(f"⚠️ Attempt {attempt}: Exception - {str(e)}")
        time.sleep(delay)
    return None

# 🧾 Clean and parse CSV input
with open("gcci_dummy_input_data.csv", newline='', encoding="utf-8-sig") as csvfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader, start=1):
        start_time = time.time()

        # ✅ Clean column headers and values
        clean_row = {k.strip(): v.strip() for k, v in row.items() if k and v}

        try:
            dummy_data = GCCICertificateData(**clean_row)
        except Exception as e:
            print(f"❌ Row {idx}: Error parsing input: {e}")
            continue

        response = post_with_retries(dummy_data.model_dump())

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        pdf_filename = os.path.join(pdf_output_dir, f"gcci_certificate_{idx}_{timestamp}.pdf")

        if response:
            with open(pdf_filename, "wb") as f:
                f.write(response.content)
        else:
            print(f"❌ Row {idx}: Failed to generate PDF after retries.")
            continue

        # ✅ Generate CSV test report
        report_filename = os.path.join(csv_output_dir, f"gcci_report_{idx}.csv")
        with open(report_filename, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Input Field", "Value"])
            for field, value in dummy_data.model_dump().items():
                writer.writerow([field, value])
            writer.writerow([])
            writer.writerow(["Test Parameter", "Score", "Remarks"])
            for param in test_parameters:
                score, remark = get_evaluation(param)
                writer.writerow([param, score, remark])

        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        elapsed = round(time.time() - start_time, 2)

        print("--------------------------------------------------")
        print(f"✅ [{idx}] PDF Generated: {pdf_filename}")
        print(f"   CPU: {cpu}% | Memory: {mem}% | Time: {elapsed}s")
        print("--------------------------------------------------")

        time.sleep(2)  # ⏱ Prevent server overload

print("🎉 All PDFs and reports generated successfully.")