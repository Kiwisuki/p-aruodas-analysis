from typing import Tuple, Dict, Any, List
from datetime import datetime
import re
import undetected_chromedriver as uc
from lxml import html
from bs4 import BeautifulSoup
from parsing_tools import extract_element, text_strip_list, extract_photos, extract_table
from parsing_tools import extract_ad_stats, extract_address, extract_number, extract_coordinates, extract_price
from parsing_tools import filter_links


def get_html(url: str) -> str:
    """Returns the HTML content of the webpage with the given URL using headless Chrome."""
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    
    driver = uc.Chrome(options=options)
    driver.get(url)
    html_content = driver.page_source
    driver.quit()
    return html_content

def scrape_property(url: str, debug=True, **kwargs: Any) -> Dict[str, Any]:
    """
    Extracts information about a property from a property listing page on aruodas.lt.

    Args:
        url (str): The url of the property listing page.

    Returns:
        Dict[str, Any]: A dictionary of the property information.
    """
    source = get_html(url)

    if debug:
        with open('debug.html', 'w') as file:
            file.write(source)
    
    tree = html.fromstring(source)
    property_info = {
        'Price': extract_price(tree),
        'Address': extract_address(tree),
        'Phone': extract_number(tree)[0],
        'Broker': extract_number(tree)[1],
        'Coordinates': extract_coordinates(tree),
        'Reserved': extract_element(tree, 'reservation-strip__text'),
        'Date_scraped': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'Description': extract_element(tree, 'collapsedText'),
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

if __name__ == '__main__':
    url = 'https://www.aruodas.lt/butu-nuoma-vilniuje-salininkuose-mechaniku-g-tvarkingas-butas-puikiai-gyventi-ar-4-1224363/'
    property_info = scrape_property(url)
    print(property_info)