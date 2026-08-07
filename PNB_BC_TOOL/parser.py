import re

def clean_lines(raw_text):
    return [line.strip() for line in raw_text.splitlines() if line.strip()]

def find_customer_block(lines):
    for i, line in enumerate(lines):
        if line.startswith("K") and len(line) > 20:
            return i
    return -1

def parse_data(raw_text):

    data = {
        "NAME": "",
        "ACCOUNT_NO": "",
        "CIF": "",
        "AADHAAR": "",
        "ADDRESS": "",
        "PIN": "",
        "FATHER_NAME": "",
        "MODE": "SELF",
        "OPEN_DATE": "",
        "ISSUE_DATE": "",
        "NOMINATION": ""
    }

    lines = clean_lines(raw_text)

    start = find_customer_block(lines)

    if start == -1:
        return data

    try:
        # Basic Details
        data["NAME"] = lines[start + 1]
        data["ACCOUNT_NO"] = lines[start + 3]
        data["CIF"] = lines[start + 4]
        data["AADHAAR"] = lines[start + 6]

        # Address
        address = lines[start + 8] + " " + lines[start + 9]

        # PIN
        pin_match = re.search(r"\b\d{6}\b", address)

        if pin_match:
            data["PIN"] = pin_match.group(0)

            # PIN ke baad ka sab hata do
            address = address.split(data["PIN"])[0]

        data["ADDRESS"] = address.strip(" ,")

    except Exception as e:
        print("Parse Error:", e)

    # Father Name
    for line in lines:
        if line.strip() == "SHEKH WASIL":
            data["FATHER_NAME"] = line.strip()
            break

    return data