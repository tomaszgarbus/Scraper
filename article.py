"""
A unified representation for article, regardless of the source. It does not
involve any understanding of the contents yet.
"""
import json
from typing import List, Dict


class BaseArticle:
    def __init__(self, name: str, nuid: str, raw_html: str):
        self.name = name
        # nuid = non-unique id (there is no uniqueness assumption)
        self.nuid = nuid
        self.raw_html = raw_html
        

class Article(BaseArticle):
    """
    A class representing an article scraped from a single webpage.
    """
    def __init__(self, title: str,
                 datetime: str,
                 text: str,
                 source_url: str,
                 raw_html: str):
        super(Article, self).__init__(name=title, id=datetime,
                                      raw_html=raw_html)
        self.title = title
        self.datetime = datetime
        self.text = text
        self.source_url = source_url

    def __str__(self):
        return '\n'.join([
            '::' + self.title + '::',
            '@' + (self.datetime or ""),
            'url: ' + self.source_url,
            self.text
        ])


class ProductWithReviews(BaseArticle):
    """
    A class representing a product from e.g. Amazon with reviews.
    """
    def __init__(self, product_name: str, product_params: Dict[str],
                 reviews: List[str], raw_html: str):
        super(ProductWithReviews, self).__init__(name=product_name,
                                                 id=product_name,
                                                 raw_html=raw_html)
        self.product_name = product_name
        self.product_params = product_params
        self.reviews = reviews

    def __str__(self):
        return json.dumps({
            'product_name': self.product_name,
            'product_params': self.product_params,
            'reviews': self.reviews
        })
