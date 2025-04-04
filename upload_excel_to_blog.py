import pandas as pd
import time
import os
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

EXCEL_FILE = "scraped_data.xlsx"
CHECKPOINT_FILE = "checkpoint.txt"
ADMIN_URL = "https://blogwebsite.url/admin"
LOGIN_URL = f"{ADMIN_URL}/login"
ADD_POST_URL = f"{ADMIN_URL}/add-post?type=article"
ADD_CATEGORY_URL = f"{ADMIN_URL}/add-category?type=parent"

EMAIL = "admin_mail"
PASSWORD = "admin_password"

HEADLESS = False  # Toggle headless mode here

def get_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def login(driver):
    driver.get(LOGIN_URL)
    driver.find_element(By.NAME, "email").send_keys(EMAIL)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.TAG_NAME, "form").submit()
    WebDriverWait(driver, 10).until(EC.url_contains("/admin"))

def get_uploaded():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_checkpoint(url):
    with open(CHECKPOINT_FILE, "a") as f:
        f.write(url + "\n")

def add_category_if_missing(driver, category):
    driver.get(ADD_CATEGORY_URL)
    time.sleep(2)
    input_box = driver.find_element(By.NAME, "name")
    input_box.clear()
    input_box.send_keys(category)
    submit = driver.find_element(By.XPATH, "//button[contains(text(),'Add Category')]")
    submit.click()
    time.sleep(2)

def select_or_add_category(driver, category):
    try:
        select = Select(driver.find_element(By.NAME, "category_id"))
        options = [opt.text.strip().lower() for opt in select.options]
        if category.lower() not in options:
            add_category_if_missing(driver, category)
            driver.get(ADD_POST_URL)
            select = Select(driver.find_element(By.NAME, "category_id"))
        select.select_by_visible_text(category)
    except Exception as e:
        print(f"❌ Category selection failed: {e}")

def insert_html_to_tinymce(driver, html_content):
    try:
        # Wait for TinyMCE to be ready
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return typeof(tinymce) !== 'undefined' && tinymce.activeEditor !== null")
        )
        driver.execute_script("tinymce.activeEditor.setContent(arguments[0])", html_content)
        time.sleep(1)
    except Exception as e:
        print(f"❌ Error writing content in TinyMCE: {e}")

def set_tags(driver, tags_str):
    try:
        tag_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".tagify__input"))
        )
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        for tag in tags:
            tag_input.send_keys(tag)
            tag_input.send_keys(Keys.ENTER)
            time.sleep(0.3)
    except Exception as e:
        print(f"❌ Error setting tags: {e}")

def post_blog(driver, row):
    driver.get(ADD_POST_URL)
    time.sleep(2)

    try:
        driver.find_element(By.NAME, "title").send_keys(row['title'])
        driver.find_element(By.NAME, "summary").send_keys(row.get('title', '')[:160])
        driver.find_element(By.NAME, "keywords").send_keys(row.get('tags', ''))
    except Exception as e:
        print(f"❌ Error filling title/summary/keywords: {e}")

    set_tags(driver, row.get('tags', ''))

    insert_html_to_tinymce(driver, row['content'])

    try:
        image_input = driver.find_element(By.ID, "video_thumbnail_url")
        driver.execute_script("arguments[0].scrollIntoView(true);", image_input)
        time.sleep(0.5)
        image_input.send_keys(row.get('image_url', ''))
    except Exception as e:
        print(f"❌ Error adding image URL: {e}")

    try:
        select_or_add_category(driver, row['category'])
    except Exception as e:
        print(f"❌ Error in category selection: {e}")

    try:
        driver.execute_script("allowSubmitForm = true;")
        submit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @name='status' and @value='1']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(1)
        submit_btn.click()
        # WebDriverWait(driver, 10).until(EC.url_contains("/admin/posts"))
        print("✅ Post published.")
    except Exception as e:
        print(f"❌ Error clicking publish button: {e}")

def main():
    df = pd.read_excel(EXCEL_FILE)
    uploaded = get_uploaded()
    driver = get_driver()
    login(driver)

    for _, row in tqdm(df.iterrows(), total=len(df)):
        if row['scrap_url'] in uploaded:
            continue
        try:
            post_blog(driver, row)
            save_checkpoint(row['scrap_url'])
        except Exception as e:
            print(f"Failed to upload {row['scrap_url']}: {e}")
            continue

    driver.quit()

if __name__ == "__main__":
    main()
