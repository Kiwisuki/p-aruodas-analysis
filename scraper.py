import logging

from retrying import retry

from db_tools import get_scraped_properties, save_property
from parsing_tools import extract_ad_id, preprocess_property
from scraping_tools import get_max_page, get_property_links, get_thumbnail_links, scrape_property
from utils import retry

TYPES = ['butai', 'butu-nuoma', 'namai', 'namu-nuoma', 'patalpos', 'patalpu-nuoma']
MAX_RETRIES = 10000


class Scraper:
    def __init__(self, ad_type: str):
        self.max_page = get_max_page(f'https://www.aruodas.lt/{ad_type}/')
        self.ad_type = ad_type
        self.page_on = 1
        self.scraped_ids = get_scraped_properties(ad_type)

    @retry(max_retries=MAX_RETRIES, wait_time=30, random_wait=True)
    def scrape(self):
        for page in range(self.page_on, self.max_page + 1):
            logging.info(f'Page {page}/{self.max_page}')
            page_url = f'https://www.aruodas.lt/{self.ad_type}/puslapis/{page}/'
            property_ids = get_property_links(page_url)
            property_ids = [extract_ad_id(link) for link in property_ids]
            property_thumbs = get_thumbnail_links(page_url) # might be useful to combine into one function

            thumbs_match = len(property_thumbs) == len(property_ids)
            if not thumbs_match:
                logging.info(f'Page {page}: Thumbs and ids do not match')

            for i, property_id in enumerate(property_ids):                
                if property_id in self.scraped_ids:
                    logging.info(f'Property {property_id} already scraped')
                    continue

                url = f'https://www.aruodas.lt/{property_id}/'
                logging.info(f'Scraping: {url}')
                
                if thumbs_match:
                    property = scrape_property(url, Thumbnail=property_thumbs[i])
                else:
                    property = scrape_property(url)

                property = preprocess_property(property)
                save_property(property, self.ad_type)
                
                
                self.scraped_ids.add(property_id)
        
        logging.info(f'Scraped {len(self.scraped_ids)} properties')
        return True


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.getLogger('undetected_chromedriver').setLevel(logging.WARNING)

    for ad_type in TYPES:
        scraper = Scraper(ad_type)
        scraper.scrape()