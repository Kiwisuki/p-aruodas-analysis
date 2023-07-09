from typing import Any, Dict, List
from datetime import datetime
import os
import re

from bs4 import BeautifulSoup
from lxml import html
import undetected_chromedriver as uc

from parsing_tools import (extract_element, text_strip_list, extract_photos, extract_table,
                           extract_ad_stats, extract_address, extract_number, extract_coordinates,
                           extract_price, filter_links, extract_by_id)
from utils import retry

MAX_HTML_RETRIES = 10
MAX_PROPERTY_RETRIES = 3
RETRY_WAIT_TIME = 10



@retry(max_retries=MAX_HTML_RETRIES, wait_time=RETRY_WAIT_TIME, random_wait=True)
def get_html(url: str, save_html: bool=False) -> str:
    """Returns the HTML content of the webpage with the given URL using headless Chrome."""
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    driver = uc.Chrome(options=options)
    driver.get(url)
    html_content = driver.page_source
    driver.quit()

    if save_html:
        # remove the protocol and www. from the url
        base_filename = re.sub(r'https?://(www\.)?', '', url)
        # remove the trailing slash
        base_filename = base_filename.rstrip('/')
        # replace slashes with underscores
        base_filename = base_filename.replace('/', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_filename}_{timestamp}.html"
        filepath = os.path.join("raw_html/", filename)
        with open(filepath, 'w') as file:
            file.write(html_content)
    return html_content

@retry(max_retries=MAX_PROPERTY_RETRIES, wait_time=RETRY_WAIT_TIME, random_wait=True)
def scrape_property(url: str, save_html: bool=True, **kwargs: Any) -> Dict[str, Any]:
    """
    Extracts information about a property from a property listing page on aruodas.lt.

    Args:
        url (str): The url of the property listing page.

    Returns:
        Dict[str, Any]: A dictionary of the property information.
    """
    source = get_html(url, save_html=save_html)
    
    tree = html.fromstring(source)
    property_info = {
        'Price': extract_price(tree),
        'Address': extract_address(tree),
        'Phone': extract_number(tree)[0],
        'Broker': extract_number(tree)[1],
        'Coordinates': extract_coordinates(tree),
        'Reserved': extract_element(tree, 'reservation-strip__text'),
        'Date_scraped': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'Description': extract_by_id(tree, 'collapsedText'),
        'Misc': text_strip_list(tree.body.find_class('special-comma')),
        'Photos': extract_photos(tree)
    }

    ad_table = extract_table(tree)
    ad_stats = extract_ad_stats(tree)

    property_info.update(ad_table)
    property_info.update(ad_stats)

    property_info.pop('Ypatybės:', None)
    property_info.pop('Papildomos patalpos:', None)
    property_info.pop('Papildoma įranga:', None)
    property_info.pop('Apsauga:', None)
    property_info = {key.replace(':', '').replace(' ', '_'): value for key, value in property_info.items()}

    for key, value in kwargs.items():
        property_info[key] = value
    return property_info

def get_property_links(url: str) -> List[str]:
    html_text = get_html(url)
    soup = BeautifulSoup(html_text, 'html.parser')
    links = soup.find_all('a')
    links = [link.get('href') for link in links]
    links = [link for link in links if 'aruodas.lt' in str(link)]
    links = filter_links(links)
    links = list(set(links))
    return links

def get_thumbnail_links(url: str) -> List[str]:
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    thumbnails = soup.find_all('div', class_='list-photo-v2')
    srcs = [thumbnail.find('img')['src'] for thumbnail in thumbnails]
    return srcs

def get_max_page(url: str) -> int:
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    buttons = soup.find_all('a', class_='page-bt')
    button_texts = [button.text for button in buttons]
    # filter with regex if contains number
    button_texts = [button_text for button_text in button_texts if re.search(r'\d', button_text)]
    # get max number
    max_page = max([int(button_text) for button_text in button_texts])
    return max_page
