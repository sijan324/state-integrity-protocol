# test_sheet.py
import requests

url = "https://script.google.com/macros/s/AKfycbydsHRacNb0e6pWgzT3L-95gBiDTo4M_6kxBuBuit2l5yHTgIW4jGnEuey8nF0qSFqJ/exec"

payload = {
    "makes_sense": "Yes",
    "use_case": "Test submission",
    "accurate": "Yes",
    "use_again": "Yes",
    "suggestion": "Testing locally",
    "status": "accepted",
    "drift": 0.34
}

r = requests.post(url, json=payload, allow_redirects=True, timeout=15)
print("Status:", r.status_code)
print("Response:", r.text)