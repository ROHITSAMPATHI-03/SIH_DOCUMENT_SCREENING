import cv2
import pytesseract
import json
import re
import os

# ============================================================
# CONFIGURATION
# ============================================================

pytesseract.pytesseract.tesseract_cmd = (r"C:\Program Files\Tesseract-OCR\tesseract.exe")
IMAGE_PATH = os.path.join("input", "passport.jpg")
OUTPUT_PATH = os.path.join("output", "ocr_data.json")

print(f"Using image: {IMAGE_PATH}")

# ============================================================
# CHECK IMAGE
# ============================================================

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise FileNotFoundError(
        f"Could not find or read image: {IMAGE_PATH}"
    )

# ============================================================
# OCR
# ============================================================

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Improve OCR quality
gray = cv2.resize(
    gray,
    None,
    fx=2,
    fy=2,
    interpolation=cv2.INTER_CUBIC
)

gray = cv2.GaussianBlur(gray, (3, 3), 0)

_, processed_image = cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY + cv2.THRESH_OTSU
)

# OCR configuration
custom_config = r'--oem 3 --psm 6'

raw_text = pytesseract.image_to_string(
    processed_image,
    config=custom_config
)

print("\n========== RAW OCR ==========\n")
print(raw_text)

# ============================================================
# CLEAN TEXT
# ============================================================

text = raw_text.upper()

# ============================================================
# FIELD EXTRACTION FUNCTIONS
# ============================================================

def clean(value):
    if value:
        value = value.strip()
        value = re.sub(r'\s+', ' ', value)
        return value
    return None


def find_first(patterns, text):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)

        if match:
            return clean(match.group(1))

    return None


# ============================================================
# PASSPORT NUMBER
# ============================================================

passport_number = find_first([
    r'Passport\s*(?:No\.?|Number)?\s*[:\-]?\s*([A-Z][A-Z0-9]{7})',
    r'Passport\s*No\.?\s*[:\-]?\s*([A-Z0-9]{8})',
    r'\b([A-Z][0-9]{7})\b'
], text)

# ============================================================
# SURNAME
# ============================================================

surname = find_first([
    r'Surname\s*[:\-]?\s*([A-Z]+)',
], text)

# ============================================================
# GIVEN NAME
# ============================================================

given_name = find_first([
    r'Given\s*Name(?:\(s\))?\s*[:\-]?\s*([A-Z][A-Z ]+)',
    r'Given\s*Names?\s*[:\-]?\s*([A-Z][A-Z ]+)'
], text)

# Remove accidental field text
if given_name:
    given_name = re.sub(
        r'\b(NATIONALITY|DATE OF BIRTH|SEX|PLACE OF BIRTH|PLACE OF ISSUE)\b.*',
        '',
        given_name
    ).strip()

# ============================================================
# NATIONALITY
# ============================================================

nationality = find_first([
    r'Nationality\s*[:\-]?\s*(INDIAN|NORWEGIAN|[A-Z]{3,})'
], text)

# ============================================================
# GENDER
# ============================================================

gender = find_first([
    r'\b([MF])\s+(?:[0-9]{2}/[0-9]{2}/[0-9]{4})',
    r'\bSex\s*[:\-]?\s*([MF])\b'
], text)

# ============================================================
# DATE OF BIRTH
# ============================================================

date_of_birth = find_first([
    r'Date\s*of\s*Birth\s*[:\-]?\s*([0-9]{2}/[0-9]{2}/[0-9]{4})',
    r'\b([0-9]{2}/[0-9]{2}/[0-9]{4})\b'
], text)

# ============================================================
# DATE OF EXPIRY
# ============================================================

date_of_expiry = find_first([
    r'Date\s*of\s*Expiry\s*[:\-]?\s*([0-9]{2}/[0-9]{2}/[0-9]{4})'
], text)

# If two dates are found, use the second as expiry
dates = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', text)

if len(dates) >= 2:
    if not date_of_birth:
        date_of_birth = dates[0]

    if not date_of_expiry:
        date_of_expiry = dates[-1]

# ============================================================
# PLACE OF BIRTH
# ============================================================

place_of_birth = find_first([
    r'Place\s*of\s*Birth\s*[:\-]?\s*([A-Z ]+)',
], text)

# ============================================================
# PLACE OF ISSUE
# ============================================================

place_of_issue = find_first([
    r'Place\s*of\s*Issue\s*[:\-]?\s*([A-Z ]+)',
], text)

# ============================================================
# DATE OF ISSUE
# ============================================================

date_of_issue = find_first([
    r'Date\s*of\s*Issue\s*[:\-]?\s*([0-9]{2}/[0-9]{2}/[0-9]{4})'
], text)

# ============================================================
# FALLBACK FOR YOUR INDIAN PASSPORT FORMAT
# ============================================================

if not passport_number:
    match = re.search(r'\b[A-Z][0-9]{7}\b', text)
    if match:
        passport_number = match.group(0)

if not surname:
    match = re.search(r'\n([A-Z]{5,})\s*\n', text)
    if match:
        surname = match.group(1)

if not nationality:
    if "INDIAN" in text:
        nationality = "INDIAN"
    elif "NORWEGIAN" in text:
        nationality = "NORWEGIAN"

if not gender:
    if re.search(r'\bINDIAN\s+F\b', text):
        gender = "F"
    elif re.search(r'\bINDIAN\s+M\b', text):
        gender = "M"

# ============================================================
# FINAL OCR DATA
# ============================================================

ocr_data = {
    "document_type": "Passport",
    "passport_number": passport_number,
    "surname": surname,
    "given_name": given_name,
    "nationality": nationality,
    "date_of_birth": date_of_birth,
    "gender": gender,
    "place_of_birth": place_of_birth,
    "place_of_issue": place_of_issue,
    "date_of_issue": date_of_issue,
    "date_of_expiry": date_of_expiry
}

# ============================================================
# DISPLAY
# ============================================================

print("\n========== EXTRACTED DATA ==========\n")

for key, value in ocr_data.items():
    print(f"{key}: {value}")

print("\n====================================")

# ============================================================
# SAVE JSON
# ============================================================

os.makedirs("output", exist_ok=True)

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        ocr_data,
        file,
        indent=4,
        ensure_ascii=False
    )

print(f"\n✅ JSON file created successfully!")
print(f"Saved to: {OUTPUT_PATH}")