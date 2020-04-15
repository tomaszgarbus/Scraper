from typing import Optional

from bs4 import BeautifulSoup

from article import BaseArticle
from configs.scraper_config import ScraperConfig


class TechradarScraperConfig(ScraperConfig):
    def home(self) -> str:
        return "https://www.techradar.com/uk/reviews"

    def domain(self) -> str:
        return "https://www.techradar.com"

    def state_cache_fname(self) -> str:
        return "techradar_state_cache"

    def should_follow_link(self, link: str) -> bool:
        return link.startswith(self.domain())

    def extract_article(self, soup: BeautifulSoup, source_url: str) -> \
            Optional[BaseArticle]:
        pass