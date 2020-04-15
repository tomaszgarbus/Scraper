from typing import Optional

import requests
from bs4 import BeautifulSoup

from article import ProductWithReviews
from configs.scraper_config import ScraperConfig


class AmazonScraperConfig(ScraperConfig):
    def __init__(self):
        super(AmazonScraperConfig, self).__init__()

    def home(self) -> str:
        return 'https://www.amazon.com/electronics-store/b/ref=dp_bc_aui_C_1?ie=UTF8&node=172282'

    def domain(self) -> str:
        return 'https://www.amazon.com'

    def fetch_page(self, page_url) -> str:
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
        headers = {'User-Agent': user_agent}
        return requests.get(page_url, headers=headers).text

    def soup_features(self) -> str:
        return 'lxml'

    def state_cache_fname(self) -> str:
        return 'amazon_state_cache'

    def should_follow_link(self, link: str) -> bool:
        return (link.startswith('https://www.amazon.com/b/ref') or
                link.startswith('https://www.amazon.com/gp/product/'))

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[ProductWithReviews]:
        if not source_url.startswith('https://www.amazon.com/gp/product/'):
            return None

        product_name = soup.find('span', attrs={'id': 'productTitle'})
        if product_name is None:
            return None
        product_name = product_name.text.strip()

        product_params = {}
        tech_details_tables = []
        tech_details_tables += soup.find_all(
            class_='productDetails_techSpec_section_1')
        tech_details_tables += soup.find_all(
            class_='productDetails_techSpec_section_2')
        tech_details_tables += soup.find_all(
            class_='productDetails_techSpec_section_3')
        for table in tech_details_tables:
            for tr in table.findall('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th is None or td is None:
                    continue
                product_params[th.text.strip()] = td.text.strip()

        reviews = []
        for review in soup.find_all(class_='aok-relative'):
            try:
                review_text = review.find('reviewText').text.strip()
                review_rating = review.find('review-rating').text.strip()
                review_rating = int(review_rating[0])
                review_votes = review.find('cr-vote-text').text.strip()
                review_votes = int(review_votes.split(' ')[0])
                reviews.append({
                    'text': review_text,
                    'rating': review_rating,
                    'votes': review_votes
                })
            except AttributeError:
                continue

        raw_html = str(soup)
        prod = ProductWithReviews(product_name, product_params,
                                  reviews, raw_html, source_url)
        return prod
