import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_chromedriver():
    """Install ChromeDriver if not already installed."""
    logger.info("Auto-installing ChromeDriver...")
    chromedriver_autoinstaller.install()

def scrape_website(website):
    """Scrape a website and return the HTML content."""
    install_chromedriver()  # Ensure ChromeDriver is installed
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode if you don’t need a visible browser
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    try:
        logger.info(f"Launching local Chrome browser to scrape {website} ...")
        # Initialize Chrome WebDriver
        with webdriver.Chrome(options=chrome_options) as driver:
            driver.get(website)

            logger.info('Navigating! Scraping page content...')
            html = driver.page_source
            return html
    
    except Exception as e:
        logger.error(f"Failed to scrape the website {website}: {str(e)}")
        raise

def extract_body_content(html_content):
    """Extract the body content from the raw HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    """Clean the extracted body content by removing unnecessary elements like script and style."""
    soup = BeautifulSoup(body_content, "html.parser")
    
    # Remove <script> and <style> tags
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
        
    # Get clean text and split into lines, removing empty lines
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    
    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    """Split the DOM content into chunks of a maximum length."""
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]
