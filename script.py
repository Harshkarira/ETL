import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import pyodbc

def download_reliance_data(username, password):
    download_dir = "/tmp"
    chrome_options = Options()
    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
        },
    )
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    print("Browser opened successfully")

    driver.get("https://www.screener.in/login/")
    time.sleep(2)
    driver.find_element(By.ID, "id_username").send_keys(username)
    driver.find_element(By.ID, "id_password").send_keys(password)
    print("Credentials entered")

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
    )
    login_button.click()
    print("Login button clicked")

    WebDriverWait(driver, 10).until(
        lambda driver: "login" not in driver.current_url.lower()
    )
    print("Logged in successfully. Current URL:", driver.current_url)

    time.sleep(2)
    driver.get("https://www.screener.in/company/RELIANCE/")
    export_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Export to Excel"]'))
    )
    export_button.click()
    print("Export button clicked")

    time.sleep(5)
    downloaded_file = os.path.join(download_dir, "Reliance Industr.xlsx")
    print(f"Excel file downloaded as: {downloaded_file}")
    driver.quit()
    return downloaded_file

def process_and_load(file_path):
    df = pd.read_excel(file_path, sheet_name=0, skiprows=2, nrows=16, usecols='B:K')
    df.columns = ['Narration', 'Mar-15', 'Mar-16', 'Mar-17', 'Mar-18', 
                  'Mar-19', 'Mar-20', 'Mar-21', 'Mar-22', 'Mar-23', 'Mar-24']
    df.dropna(subset=['Narration'], inplace=True)

    melted_df = pd.melt(
        df,
        id_vars=['Narration'],
        value_vars=[col for col in df.columns if col.startswith('Mar')],
        var_name='date',
        value_name='value'
    )
    melted_df['type'] = melted_df['Narration']
    melted_df['date'] = melted_df['date'].apply(lambda x: datetime.strptime(f"31-{x}", "%d-Mar-%y"))
    melted_df['id'] = melted_df.index + 1  # Simple ID generation
    melted_df = melted_df[['id', 'date', 'type', 'value']]

    melted_df['value'] = pd.to_numeric(
        melted_df['value'].astype(str).str.replace(',', '').str.replace('%', ''),
        errors='coerce'
    )

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=mssql:1433;"
        "DATABASE=KafkaDB;"
        "UID=sa;"
        "PWD=P@ssW0rdS3cuR3!"
    )
    cursor = conn.cursor()

    for _, row in melted_df.iterrows():
        cursor.execute(
            "INSERT INTO source_table (id, date, type, value) VALUES (?, ?, ?, ?)",
            row['id'], row['date'], row['type'], row['value']
        )
    conn.commit()

def main():
    try:
        username = os.environ["USERNAME"]
        password = os.environ["PASSWORD"]
        excel_file = download_reliance_data(username, password)
        process_and_load(excel_file)
        print(f"Processed and loaded: {excel_file}")
    except Exception as e:
        print(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    main()