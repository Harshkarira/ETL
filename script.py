import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def download_reliance_data(username, password):
    try:
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
            EC.element_to_be_clickable(
                (By.XPATH, '//button[@aria-label="Export to Excel"]')
            )
        )
        export_button.click()
        print("Export button clicked")

        time.sleep(5)
        downloaded_file = "Reliance Industr.xlsx"
        print(f"Excel file downloaded as: {downloaded_file}")
        return downloaded_file

    except Exception as e:
        print(f"Error downloading the file: {e}")
        print("Current URL at failure:", driver.current_url)
        raise

    finally:
        driver.quit()

file_name = 'Reliance Industr.xlsx'
try:
    df = pd.read_excel(
        file_name,
        sheet_name=0,
        skiprows=2,
        nrows=16,
        usecols='B:K'
    )

    df.columns = ['Narration', 'Mar-15', 'Mar-16', 'Mar-17', 'Mar-18', 
                 'Mar-19', 'Mar-20', 'Mar-21', 'Mar-22', 'Mar-23', 'Mar-24']
    
    df.dropna(subset=['Narration'])

    for col in df.columns[1:]:  # Skip 'Narration' column
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(',', '').str.replace('%', ''),
            errors='coerce'
        ) / (100 if df.loc[df['Narration'].isin(['Dividend Payout', 'OPM']), col].any() else 1)

    print("First few rows of the DataFrame:")
    print(df.head())
    print("\nDataFrame Info:")
    print(df.info())
    print("\nShape of DataFrame:", df.shape)
    
except FileNotFoundError:
    print(f"Error: The file '{file_name}' was not found in the current directory")
except Exception as e:
    print(f"Error occurred while reading the file: {str(e)}")

def main():
    try:
        username = os.environ["USERNAME"]
        password = os.environ["PASSWORD"]
        excel_file = download_reliance_data(username, password)
        print(f"Download successful: {excel_file}")
    except KeyError as e:
        print(f"Environment variable missing: {e}")
        raise
    except Exception as e:
        print(f"Script failed: {e}")
        raise


if __name__ == "__main__":
    main()