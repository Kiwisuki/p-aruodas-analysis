from typing import Tuple, Dict, Any, List
from datetime import datetime
import re
import undetected_chromedriver as uc
from lxml import html
from parsing_tools import extract_element, text_strip_list, extract_photos, extract_table, extract_ad_stats, extract_address, extract_number, extract_coordinates


def get_html(url: str) -> str:
    """Returns the HTML content of the webpage with the given URL using headless Chrome."""
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    with uc.Chrome(options=options) as driver:
        driver.get(url)
        html_content = driver.page_source
    return html_content

def scrape_property(url: str) -> Dict[str, Any]:
    """
    Extracts information about a property from a property listing page on aruodas.lt.

    Args:
        url (str): The url of the property listing page.

    Returns:
        Dict[str, Any]: A dictionary of the property information.
    """
    source = get_html(url)
    tree = html.fromstring(source)
    property_info = {
        'Price': extract_element(tree, 'price-eur'),
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
    return property_info


if __name__ == '__main__':
    url = 'https://www.aruodas.lt/butu-nuoma-vilniuje-salininkuose-mechaniku-g-tvarkingas-butas-puikiai-gyventi-ar-4-1224363/'
    property_info = parse_property(url)
    print(property_info)