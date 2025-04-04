# 🕷️ Downloadly Scrapper Bot + Blog Uploader

This project automates scraping blog content from a Downloadly-based site and uploading it to a custom blog website via its admin panel.

## 📁 Features

- Scrapes blog post data (title, image, content, categories, tags) from sitemap URLs.
- Cleans unwanted elements from post content.
- Saves the scraped data to an Excel file.
- Uses Selenium to log into a custom admin panel and auto-fill blog post details.
- Handles:
  - TinyMCE content editor
  - Tag input fields
  - Category creation (if not already present)
  - Upload progress with resume capability

---

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rijj1/downloadly-scrapper-bot.git
   cd downloadly-scrapper-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📂 Project Structure

```
├── downloadly_scrapper_bot.py     # Scrapes posts from sitemap URLs
├── upload_excel_to_blog.py        # Uploads Excel content to WordPress-like blog
├── sitemap.csv                    # List of sitemap URLs
├── scraped_data.xlsx              # Output file (auto-generated)
├── checkpoint.txt                 # Tracks uploaded posts (auto-generated)
├── requirements.txt               # Python dependencies
```

---

## ⚙️ Usage

### Step 1: Scrape blog post data

Update `sitemap.csv` with sitemap URLs (one per line), then run:

```bash
python downloadly_scrapper_bot.py
```

This will generate `scraped_data.xlsx` containing all post data.

### Step 2: Upload to your blog

Edit `upload_excel_to_blog.py` and set the following:
```python
EMAIL = "your_admin_email"
PASSWORD = "your_admin_password"
ADMIN_URL = "https://your-site.com/admin"
```

To enable headless browser mode:
```python
HEADLESS = True
```

Then run:
```bash
python upload_excel_to_blog.py
```

Uploaded URLs are saved to `checkpoint.txt` so they won’t be re-uploaded on subsequent runs.

---

## 🧠 Notes

- Supports dynamic category addition if it doesn’t exist.
- Handles delays and scrolls to avoid interaction issues.
- Compatible with TinyMCE editors and tagify-style tag inputs.

---

## 🔒 Disclaimer

This project is intended for educational purposes and for automating content you own or have permission to use. Scraping copyrighted material or abusing admin panel access may violate terms of service.

---

## 👨‍💻 Author

Made by Rijwan Ansari  
Contributions welcome!
**
