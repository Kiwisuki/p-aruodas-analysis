from datetime import datetime
from typing import Any, Dict, List, Tuple
import logging

from lxml import html
import re
import undetected_chromedriver as uc

from utils import exception_handler



def filter_links(links: List[str]) -> List[str]:
    filtered_links = []
    pattern = r'\d-\d{7}'  # Regular expression pattern for the format n-nnnnnnn

    for link in links:
        if re.search(pattern, link):
            filtered_links.append(link)

    return filtered_links

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

@exception_handler
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
    
@exception_handler
def extract_by_id(tree: html.HtmlElement, div_id: str) -> str:
    desc = tree.get_element_by_id(div_id)
    return desc.text_content()
    
@exception_handler
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

@exception_handler
def extract_thumbs(tree: html.HtmlElement) -> List[str]:
    """Extracts and returns a list of URLs for the thumbnail images in the given HTML tree."""
    thumbs = tree.find_class('link-obj-thumb')
    thumbs = [thumb.get('href') for thumb in thumbs]
    thumbs = set(thumbs)
    thumbs.discard(None)
    return thumbs

@exception_handler
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

@exception_handler
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

@exception_handler
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

@exception_handler
def extract_address(tree: html.HtmlElement) -> str:
    """
    Extracts the address of the property from the HTML tree.
    """
    address = tree.find_class('obj-header-text')[0].text_content().strip()
    address = re.split(', \d+ kamb', address)[0]
    return address

@exception_handler
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

@exception_handler
def extract_ad_stats(tree: html.HtmlElement) -> Dict[str, str]:
    """
    Extract the ad stats information from the HTML tree.
    Returns a dictionary containing the ad stats information.
    """
    ad_stats_dict = {}

    try:
        ad_stats_names = text_strip_list(tree.find_class('obj-stats simple')[0].find('dl').findall('dt'))
        ad_stats_values = text_strip_list(tree.find_class('obj-stats simple')[0].find('dl').findall('dd'))
    except IndexError:
        try:
            ad_stats_names = text_strip_list(tree.find_class('obj-stats')[0].find('dl').findall('dt'))
            ad_stats_values = text_strip_list(tree.find_class('obj-stats')[0].find('dl').findall('dd'))
        except IndexError:
            ad_stats_dict['Nuoroda'] = extract_element(tree, 'project__advert-info__value')

            ad_stats_names = []
            ad_stats_values = []
    for i, name in enumerate(ad_stats_names):
            ad_stats_dict[name] = ad_stats_values[i]
    return ad_stats_dict

@exception_handler
def extract_price(tree: html.HtmlElement) -> str:
    """
    Extracts the price of the property from the HTML tree.
    Returns the price as a string.
    """
    return extract_element(tree, 'price-eur') # for easier error handlin later on

def extract_ad_id(string: str) -> str:
    pattern = r"\d-\d{7}"
    matches = re.findall(pattern, string)
    if matches:
        return matches[0]
    else:
        return None
    

def preprocess_property(property: Dict) -> Dict:
    rename_dict = {
        'Namo_numeris': 'House_number',
        'Plotas': 'Area',
        'Kambarių_sk.': 'Number_of_rooms',
        'Aukštas': 'Floor',
        'Aukštų_sk.': 'Number_of_floors',
        'Metai': 'Year',
        'Pastato_tipas': 'Building_type',
        'Šildymas': 'Heating',
        'Įrengimas': 'Furnishing',
        'Pastato_energijos_suvartojimo_klasė': 'Energy_consumption_class',
        'Nuoroda': 'Link',
        'Įdėtas': 'Uploaded',
        'Redaguotas': 'Edited',
        'Aktyvus_iki': 'Active_until',
        'Įsiminė': 'Saved',
        'Peržiūrėjo': 'Viewed',
        'Sklypo_plotas': 'Plot_area',
        'Namo_tipas': 'House_type',
        'Artimiausias_vandens_telkinys': 'Nearest_water_reservoir',
        'Iki_vandens_telkinio_(m)': 'Distance_to_water_reservoir', 
        
    }
    # renamee keys if in rename_dict else keep the same
    property = {rename_dict[key] if key in rename_dict else key: property[key] for key in property.keys()}

    # remove symbol and convert to float
    if 'Price' in property:
        property['Price'] = int(property['Price'].replace(' €', '').replace(' ', ''))

    if 'Area' in property:
        property['Area'] = float(property['Area'].replace(' m²', '').replace(',', '.'))

    if 'Number_of_floors' in property:
        property['Number_of_floors'] = int(property['Number_of_floors'])

    if 'Number_of_rooms' in property:
        property['Number_of_rooms'] = int(property['Number_of_rooms'])

    if 'Year' in property:
        try:
            property['Year'] = int(property['Year'])
        except ValueError:
            years = re.findall(r'\d{4}', property['Year'])

            property['Year'] = int(years[0])
            property['Renovation_year'] = int(years[1])

    if 'Viewed' in property:
        property['Viewed'] = int(property['Viewed'].split('/')[0])

    if 'Saved' in property:
        property['Saved'] = int(property['Saved'])

    # convert to datetime
    if 'Uploaded' in property:
        property['Uploaded'] = datetime.strptime(property['Uploaded'], '%Y-%m-%d')

    if 'Edited' in property:
        property['Edited'] = datetime.strptime(property['Edited'], '%Y-%m-%d')

    if 'Active_until' in property:
        property['Active_until'] = datetime.strptime(property['Active_until'], '%Y-%m-%d')

    if 'Date_scraped' in property:
        property['Date_scraped'] = datetime.strptime(property['Date_scraped'], '%d/%m/%Y %H:%M:%S')

    if 'Address' in property:
        property['City'] = property['Address'].split(',')[0]

    if 'Reserved' in property:
        property['Reserved'] = property['Reserved'] != ''

    if 'Distance_to_water_reservoir' in property:
        property['Distance_to_water_reservoir'] = int(property['Distance_to_water_reservoir'].replace(' ', ''))

    if 'Link' in property:
        property['_id'] = extract_ad_id(property['Link'])

    if 'Floor' in property:
        try:
            property['Floor'] = int(property['Floor'])
        except Exception as e:
            logging.error(f'Error converting floor to int: {e}')

    return property