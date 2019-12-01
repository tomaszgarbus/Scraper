import re
from typing import Optional

from bs4 import BeautifulSoup

from article import Article
from configs.scraper_config import ScraperConfig


class PAPScraperConfig(ScraperConfig):
    def __init__(self):
        super(PAPScraperConfig, self).__init__()

    def home(self) -> str:
        return 'https://www.pap.pl'

    def domain(self) -> str:
        return 'https://www.pap.pl'

    def state_cache_fname(self) -> str:
        return 'pap_state_cache'

    def should_follow_link(self, link: str) -> bool:
        return link.startswith(self.home())

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        title = soup.find('title').text
        datetime_node = soup.find(class_='moreInfo')
        if datetime_node is None:
            return None
        datetime = datetime_node.text
        datetime = re.sub('(\n|\s)', '', datetime)
        text_node = soup.find('article', attrs={'role': 'article'})
        if text_node is None:
            return None
        text = text_node.text
        raw_html = str(soup)
        return Article(title, datetime, text, source_url, raw_html)
