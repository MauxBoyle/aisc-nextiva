import imaplib
import email
import re
import csv
import time
from itertools import batched
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# --- CONFIGURATION ---
EMAIL_USER = 'boyle@aisc.org'
EMAIL_PASS = 'REDACTED' # Use a Google App Password, not your regular password
IMAP_SERVER = 'imap.gmail.com'
NEXTIVA_SENDER = 'analytics@nextiva.com'

def get_latest_nextiva_url():
    """Logs into Gmail and finds the most recent link from Nextiva."""
    print("Searching Gmail for the latest report link...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")

    # Search for emails from Nextiva with the specific subject
    status, messages = mail.search(None, f'FROM "{NEXTIVA_SENDER}" SUBJECT "Susan Thomas has shared Missed Calls with you"')
    
    if status != 'OK' or not messages[0]:
        print("No Nextiva emails found.")
        return None

    # Get the ID of the latest email
    latest_msg_id = messages[0].split()[-1]
    status, data = mail.fetch(latest_msg_id, "(RFC822)")
    
    for response_part in data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            # 'ignore' tells Python to just skip characters it doesn't understand 
            # instead of crashing the whole script.
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

            #print("--- DEBUG: EMAIL BODY START ---")
            #print(body) # This will show us exactly what the email looks like
            #print("--- DEBUG: EMAIL BODY END ---")
            
            # This looks for the "ct.nextiva.com" link inside the HTML href attribute
            url_match = re.search(r'href=(https://ct\.nextiva\.com/ls/click\?upn=\S+)>Missed Calls</a>', body)

            if url_match:
                # url_match.group(1) grabs just the URL inside the parentheses above
                return url_match.group(1)
    
    return None

def fetch_web_data(url):
    """Uses Selenium to open the dynamic report and grab the text."""
    print(f"Opening report: {url}")
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox") # Add this
    options.add_argument("--disable-dev-shm-usage") # Add this
    options.add_argument("--disable-gpu") # Vital for Linux environments
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        time.sleep(6) # Give the Nextiva dashboard a moment to load the table
        return driver.find_element(By.TAG_NAME, "body").text
    finally:
        driver.quit()

def parse_duration(duration_str):
    """Your updated logic to handle seconds, minutes, and hours."""
    total_seconds = 0
    parts = re.findall(r'(\d+)([hms])', duration_str)
    for value, unit in parts:
        if unit == 'h': total_seconds += int(value) * 3600
        elif unit == 'm': total_seconds += int(value) * 60
        elif unit == 's': total_seconds += int(value)
    return total_seconds

def main():
    # 1. Automate the Email Link Extraction
    url = get_latest_nextiva_url()
    if not url:
        return

    # 2. Automate the Browser Data Fetching
    raw_text = fetch_web_data(url)
    
    # 3. Parse and Clean the Data
    lines = raw_text.splitlines()
    # Note: You may need to adjust this del count based on the live site layout
    if len(lines) > 10:
        del lines[:2] 
        lines.pop()

    processed_data = []
    for batch in batched(lines, 7):
        if len(batch) < 7: continue
        row = list(batch)
        row[2] = parse_duration(row[2])
        processed_data.append(row)

    # 4. Save to Master CSV
    if processed_data:
        with open('NextivaCallData.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(processed_data)
        print(f"Success! Processed {len(processed_data)} records.")

if __name__ == "__main__":
    main()