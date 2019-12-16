from typing import Optional

from bs4 import BeautifulSoup

from article import Article
from configs.scraper_config import ScraperConfig


class SportOnetPlScraperConfig(ScraperConfig):
    def home(self) -> str:
        return 'https://sport.onet.pl/pilka-nozna'

    def domain(self) -> str:
        return 'https://sport.onet.pl'

    def state_cache_fname(self) -> str:
        return 'onetsportpl_state_cache'

    def should_follow_link(self, link: str) -> bool:
        return link.startswith(self.home())

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[Article]:
        title_node = soup.find('h1', class_='mainTitle')
        if title_node is None:
            return None
        title = title_node.text.strip()
        datetime = soup.find(attrs={'itemprop': 'datePublished'}).attrs['content']
        text = soup.find(class_='whitelistPremium').text
        raw_html = str(soup)
        return Article(title, datetime, text, source_url, raw_html)
