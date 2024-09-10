# scraper.py
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_random_user_agent():
    """Returns a random user agent string to mimic different browsers."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36 Edg/91.0.864.48"
    ]
    return random.choice(user_agents)


def construct_jumia_url(product_name: str, minimum_price=0, maximum_price=None, discount_percentage=None, shipped_from_abroad: bool = False) -> str:
    """Constructs the Jumia search URL based on the specified parameters."""
    product_query = product_name.replace(" ", "+")
    url = f"https://www.jumia.com.ng/catalog/?q={product_query}"

    if maximum_price is not None:
        url += f"&price={minimum_price}-{maximum_price}"
    elif minimum_price > 0:
        url += f"&price={minimum_price}-"

    if discount_percentage is not None:
        discount_percentage = max(10, min(int(discount_percentage), 50))
        url += f"&price_discount={discount_percentage}-100"

    if shipped_from_abroad:
        url += "&shipped_from=jumia_global"

    url += "#catalog-listing"
    return url


def collect_product_links_and_data(driver) -> list:
    """Collects product links and data from the Jumia page."""
    products = []
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'prd')))
    product_elements = driver.find_elements(By.CLASS_NAME, 'prd')

    for product_element in product_elements:
        try:
            product_link = product_element.find_element(By.CLASS_NAME, 'core').get_attribute('href')
            name = product_element.find_element(By.CLASS_NAME, 'name').text
            price = product_element.find_element(By.CLASS_NAME, 'prc').text

            try:
                review_text = product_element.find_element(By.CLASS_NAME, 'rev').text
                review, number_of_reviews = review_text.split('\n')
                number_of_reviews = int(number_of_reviews.strip('()'))
            except NoSuchElementException:
                review = "No reviews"
                number_of_reviews = 0

            products.append({
                "name": name,
                "price": price,
                "review": review,
                "number_of_reviews": number_of_reviews,
                "product_link": product_link
            })

        except (StaleElementReferenceException, NoSuchElementException):
            continue

    # Sort products by review value in descending order and get the top five
    top_products = sorted(products, key=lambda x: float(x['review'].split()[0]) if 'out of' in x['review'] else 0.0, reverse=True)[:5]
    return top_products


def extract_product_description(driver, product_link: str) -> str:
    """Extracts the product description from the product link."""
    try:
        driver.get(product_link)
        wait = WebDriverWait(driver, 10)

        try:
            description_div = driver.find_element(By.ID, 'description')
            markup_div = description_div.find_element(By.XPATH, "following-sibling::div[contains(@class, 'markup')]")
            description = markup_div.text.strip()
        except NoSuchElementException:
            description = "Description not available"

        return description
    except (TimeoutException, StaleElementReferenceException) as e:
        print(f"Error extracting product description: {e}")
        return "Description not available"


def product_scrape(product_name: str, minimum_price=0, maximum_price=None, discount_percentage=None, shipped_from_abroad: bool = False) -> list:
    """Main function to scrape product details based on provided parameters."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={get_random_user_agent()}")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        url = construct_jumia_url(
            product_name, minimum_price, maximum_price, discount_percentage, shipped_from_abroad
        )
        driver.get(url)

        # Collect product links and basic data
        top_products = collect_product_links_and_data(driver)

        # Fetch descriptions for the top products
        for product in top_products:
            product['description'] = extract_product_description(driver, product['product_link'])

        return top_products

    except Exception as e:
        print(f"Error in retrieving products: {e}")
        return []

    finally:
        driver.quit()
