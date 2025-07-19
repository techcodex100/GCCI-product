import os
import time
import datetime
import requests
import psutil
from faker import Faker
from main import CertificateOfOriginData

fake = Faker()

pdf_output_dir = "rendered_gcci_pdfs"
os.makedirs(pdf_output_dir, exist_ok=True)

RENDER_URL = "https://gcci-product-1.onrender.com/generate-origin-certificate-pdf/"
DELAY_BETWEEN_REQUESTS = 5  # seconds between each attempt
TOTAL_PDFS = 50

def generate_dummy_data():
    return CertificateOfOriginData(
        exporter_name_address=fake.company() + "\n" + fake.address(),
        certificate_number=f"GCCI-{fake.random_number(digits=5)}",
        consignee_name_address=fake.company() + "\n" + fake.address(),
        transport_details="Transported by " + fake.word(),
        official_use="Verified by GCCI",
        item_number=str(fake.random_number(digits=3)),
        package_marks="Mark-" + str(fake.random_number(digits=4)),
        package_description=fake.text(max_nb_chars=60),
        origin_criteria="Made in India",
        gross_weight=f"{fake.random_int(min=100, max=1000)} kg",
        invoice_number_date=f"INV-{fake.random_number(digits=4)} dated {fake.date()}",
        hs_code=str(fake.random_number(digits=6)),
        certificate_place_date=fake.city() + ", " + fake.date(),
        certificate_signature=fake.name(),
        exporter_declaration_place_date=fake.city() + ", " + fake.date(),
        exporter_signature=fake.name(),
        importing_country=fake.country()
    )

def generate_pdf(i, data):
    attempt = 0
    while True:
        attempt += 1
        try:
            response = requests.post(RENDER_URL, json=data.model_dump())
            if response.status_code == 200:
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                filename = os.path.join(pdf_output_dir, f"gcci_certificate_{i}_{timestamp}.pdf")
                with open(filename, "wb") as f:
                    f.write(response.content)

                elapsed = round(time.time() - start_time, 2)
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent

                print(f"✅ PDF {i} generated successfully on attempt {attempt}")
                print(f"   ⏱ Time: {elapsed}s | 🧠 CPU: {cpu}% | 💾 RAM: {mem}%")
                print("-" * 50)
                return
            else:
                print(f"⚠️ Attempt {attempt}: Server responded with status {response.status_code}")
        except Exception as e:
            print(f"🚫 Attempt {attempt}: Exception occurred - {e}")

        time.sleep(DELAY_BETWEEN_REQUESTS)

# 🌀 Generate all 50 PDFs — no skip, guaranteed
for i in range(1, TOTAL_PDFS + 1):
    dummy_data = generate_dummy_data()
    start_time = time.time()
    generate_pdf(i, dummy_data)
    time.sleep(DELAY_BETWEEN_REQUESTS)

print("🎉 All 50 PDFs successfully generated without skipping.")
