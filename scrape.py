import httpx
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Set up logging for better error tracking
logging.basicConfig(level=logging.INFO)

def safe_api_call(url, retries=3, timeout=10):
    """Function to safely make API calls with retries and timeout"""
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url)
                response.raise_for_status()  # Raise an exception for 4xx/5xx errors
                return response
        except httpx.RequestError as e:
            logging.error(f"Request error: {e}, attempt {attempt + 1}/{retries}")
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
            else:
                raise  # Reraise the error after final attempt
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error: {e}")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            break
    return None

def scrape_website(website):
    logging.info("Launching local Chrome browser ...")
    
    # Set up options for headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Initialize the Chrome WebDriver with the options
    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get(website)
        logging.info(f"Scraping content from {website}...")
        html = driver.page_source
        return html

def extract_body_content(html_content):
    """Extract body content from HTML"""
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    """Clean body content by removing unnecessary tags and text"""
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(line.strip() for line in cleaned_content.splitlines() if line.strip())
    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    """Split DOM content into chunks for easier processing"""
    return [dom_content[i:i + max_length] for i in range(0, len(dom_content), max_length)]
