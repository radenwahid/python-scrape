from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def scrape_website(website):
    print("Launching local Chrome browser ...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode if you don’t need a visible browser
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Initialize local Chrome WebDriver
    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get(website)

        # Optional: handle CAPTCHA, but you'll need a third-party CAPTCHA-solving service if CAPTCHA appears
        # print('Waiting for captcha to solve...')
        # You may implement CAPTCHA handling here if needed

        print('Navigating! Scraping page content...')
        html = driver.page_source
        return html

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")
    
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
        
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    
    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length) 
    ]
