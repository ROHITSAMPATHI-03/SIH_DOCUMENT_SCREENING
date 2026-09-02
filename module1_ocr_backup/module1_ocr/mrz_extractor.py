import json
import os

import pytesseract
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

from passporteye import read_mrz

# ============================================================
# CONFIGURATION
# ============================================================

IMAGE_PATH = os.path.join("input", "passport.jpg")
OUTPUT_PATH = os.path.join("output", "mrz_data.json")

print(f"Using image: {IMAGE_PATH}")

# ============================================================
# CHECK IMAGE
# ============================================================

if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError(
        f"Passport image not found: {IMAGE_PATH}"
    )

# ============================================================
# READ MRZ
# ============================================================

print("\nReading passport MRZ...\n")

mrz = read_mrz(IMAGE_PATH)

if mrz is None:
    print("❌ MRZ could not be detected.")
    exit()

# Convert PassportEye object to dictionary
data = mrz.to_dict()

# ============================================================
# EXTRACT VALUES
# ============================================================

passport_number = data.get("number")
surname = data.get("surname")
given_name = data.get("names")
nationality = data.get("nationality")
date_of_birth = data.get("date_of_birth")
gender = data.get("sex")
date_of_expiry = data.get("expiration_date")

# ============================================================
# FORMAT DATES
# ============================================================

def format_mrz_date(date):
    if not date or len(date) != 6:
        return None

    year = int(date[:2])
    month = date[2:4]
    day = date[4:6]

    # Passport MRZ century handling
    if year >= 50:
        full_year = 1900 + year
    else:
        full_year = 2000 + year

    return f"{day}/{month}/{full_year}"


dob_formatted = format_mrz_date(date_of_birth)
expiry_formatted = format_mrz_date(date_of_expiry)

# ============================================================
# CLEAN DATA
# ============================================================

mrz_data = {
    "document_type": "Passport",
    "mrz_type": data.get("type"),
    "passport_number": passport_number,
    "surname": surname,
    "given_name": given_name,
    "nationality": nationality,
    "date_of_birth": date_of_birth,
    "date_of_birth_formatted": dob_formatted,
    "gender": gender,
    "date_of_expiry": date_of_expiry,
    "date_of_expiry_formatted": expiry_formatted,
    "mrz_valid_score": data.get("valid_score"),
    "valid_passport_number": data.get("valid_number"),
    "valid_date_of_birth": data.get("valid_date_of_birth"),
    "valid_date_of_expiry": data.get("valid_expiration_date")
}

# ============================================================
# DISPLAY
# ============================================================

print("========== CLEAN MRZ DATA ==========")

for key, value in mrz_data.items():
    print(f"{key}: {value}")

print("====================================")

# ============================================================
# SAVE
# ============================================================

os.makedirs("output", exist_ok=True)

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        mrz_data,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\n✅ MRZ JSON created successfully!")
print(f"Saved to: {OUTPUT_PATH}")