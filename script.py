import hvac
import time
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def get_vault_cred():
    try:
        client = hvac.Client(url="http://localhost:8200", token="root-token")
        if not client.is_authenticated():
            raise Exception("Vault authentication failed")

        secret = client.secrets.kv.v2.read_secret_version(
            path="screener", mount_point="secret"
        )

        username = secret["data"]["data"]["username"]
        password = secret["data"]["data"]["password"]

        return username, password

    except Exception as e:
        print(f"Error fetching vault credentials: {e}")
        raise


def download_reliance_data(username, password):
    try:
        download_dir = r"C:\Users\Harsh.karira\Desktop\vault"
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
            },
        )
        # chrome_options.add_argument('--headless')
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


def main():
    try:
        username, password = get_vault_cred()
        excel_file = download_reliance_data(username, password)
        print(f"Download successful: {excel_file}")
    except Exception as e:
        print(f"Script failed: {e}")
        raise


if __name__ == "__main__":
    main()
