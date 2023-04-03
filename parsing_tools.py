import undetected_chromedriver as uc
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from lxml import html


def while_replace(string: str) -> str:
    """
    Replace multiple consecutive spaces with a single space.
    """
    while '  ' in string:
        string = string.replace('  ', ' ')
    return string

def text_strip_list(element_list: List[html.HtmlElement]) -> List[str]:
    """Returns a list of text content stripped from the given list of HTML elements."""
    return [element.text_content().strip() for element in element_list]



def extract_element(tree: html.HtmlElement, class_name: str, index: int = 0) -> str:
    """
    Extracts the text content of an HTML element with the given class name.
    Returns an empty string if the element does not exist.
    """
    elements = tree.body.find_class(class_name)
    if elements:
        return elements[index].text.strip()
    else:
        return ""
    

def extract_table(tree: html.HtmlElement) -> Dict[str, str]:
    """
    Extracts the table information from the HTML tree.
    Returns a dictionary containing the table information.
    """
    table_dict = {}
    table_elements = tree.body.find_class('obj-details')[0].findall('dd')
    table_names = text_strip_list(tree.body.find_class('obj-details')[0].findall('dt'))
    table_names = [name for name in table_names if name != '']
    for i, name in enumerate(table_names):
        table_dict[name] = table_elements[i].text.strip()
    return table_dict


def extract_thumbs(tree: html.HtmlElement) -> List[str]:
    """Extracts and returns a list of URLs for the thumbnail images in the given HTML tree."""
    thumbs = tree.find_class('link-obj-thumb')
    thumbs = [thumb.get('href') for thumb in thumbs]
    thumbs = set(thumbs)
    thumbs.discard(None)
    return thumbs


def extract_photos(tree: html.HtmlElement) -> List[str]:
    """
    Extracts and returns a list of URLs for the photos in the given HTML tree.
    Filters out URLs that do not contain 'img.dgn'.
    """
    urls = extract_thumbs(tree)
    photos = []
    for url in urls:
        if 'img.dgn' in url:
            photos.append(url)
    return photos

def extract_coordinates(tree: html.HtmlElement) -> Tuple[float, float]:
    '''
    Extracts and returns the coordinates of the property from the given HTML tree.
    '''
    urls = extract_thumbs(tree)
    pattern = r'\d{2}\.\d+'
    for url in urls:
        if 'maps' in url:
            match = re.findall(pattern, url)
            return (float(match[0]), float(match[1]))
    return None

def extract_number(tree: html.HtmlElement) -> Tuple[str, bool]:
    """
    Extracts the phone number and broker status from the HTML tree.
    """
    try:
        phone = extract_element(tree, 'phone_item_0')
        broker = True
    except Exception as e:
        print(e)
        phone = extract_element(tree, 'phone')
        broker = False
    return phone, broker


def extract_address(tree: html.HtmlElement) -> str:
    """
    Extracts the address of the property from the HTML tree.
    """
    address = tree.find_class('obj-header-text')[0].text_content().strip()
    address = re.split(', \d+ kamb', address)[0]
    return address


def extract_table(tree: html.HtmlElement) -> Dict[str, str]:
    """
    Extract the table information from the HTML tree.
    Returns a dictionary containing the table information.
    """
    table_dict = {}
    table_elements = tree.body.find_class('obj-details')[0].findall('dd')
    table_names = text_strip_list(tree.body.find_class('obj-details')[0].findall('dt'))
    table_names = [name for name in table_names if name != '']
    for i, name in enumerate(table_names):
        table_dict[name] = table_elements[i].text.strip()
    return table_dict

def extract_ad_stats(tree: html.HtmlElement) -> Dict[str, str]:
    """
    Extract the ad stats information from the HTML tree.
    Returns a dictionary containing the ad stats information.
    """
    ad_stats_dict = {}
    ad_stats_names = text_strip_list(tree.find_class('obj-stats simple')[0].find('dl').findall('dt'))
    ad_stats_values = text_strip_list(tree.find_class('obj-stats simple')[0].find('dl').findall('dd'))
    for i, name in enumerate(ad_stats_names):
        ad_stats_dict[name] = ad_stats_values[i]
    return ad_stats_dict