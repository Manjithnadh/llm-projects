from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from langchain.tools import tool
import chromedriver_autoinstaller # Import the autoinstaller

@tool("scrape_with_selenium_tool")
def scrape_with_selenium_tool(url: str) -> str:
    """
    Scrapes and returns the HTML content of a webpage using Selenium.
    This tool is useful for getting the full content of a dynamic webpage
    that might require JavaScript rendering.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        str: The HTML content of the page, or an error message if scraping fails.
             Content is truncated to 5000 characters to avoid excessively large outputs.
    """
    # --- AUTOMATICALLY INSTALL/UPDATE CHROMEDRIVER ---
    try:
        chromedriver_autoinstaller.install()
        print("ChromeDriver installed/updated successfully.")
    except Exception as e:
        # This catch is for issues with the autoinstaller itself
        return f"Error during ChromeDriver auto-installation: {str(e)}. Please ensure Chrome browser is installed."

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu") # Recommended for headless mode
    chrome_options.add_argument("--window-size=1920,1080") # Set a default window size
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3") # Suppress verbose logging from Chrome

    driver = None # Initialize driver to None
    try:
        # Initialize the Chrome WebDriver. `chromedriver_autoinstaller` handles the path.
        driver = webdriver.Chrome(options=chrome_options)
        print(f"Attempting to navigate to URL: {url}")
        driver.get(url)

        # A small implicit wait can help with dynamic content, adjust as needed.
        driver.implicitly_wait(5) # waits up to 5 seconds for elements to be found

        html = driver.page_source
        print(f"Successfully scraped content from {url}.")
        return html[:5000] # Truncate content to avoid very long outputs
    except WebDriverException as e:
        # Catch specific Selenium WebDriver exceptions for better messages
        return f"WebDriver error during scraping {url}: {e}. Ensure Chrome is installed and updated."
    except NoSuchWindowException:
        return f"Scraping failed for {url}: Browser window closed unexpectedly. Check URL validity."
    except Exception as e:
        # Catch any other unexpected errors
        return f"An unexpected error occurred during scraping {url}: {str(e)}"
    finally:
        # Always quit the driver to free up resources
        if driver:
            driver.quit()
            print(f"Driver for {url} quit successfully.")