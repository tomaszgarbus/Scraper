class Article:
    """
    A class representing an article scraped from a single webpage.
    """
    def __init__(self, title: str,
                 datetime: str,
                 text: str,
                 source_url: str):
        self.title = title
        self.datetime = datetime
        self.text = text
        self.source_url = source_url

    def __str__(self):
        return '\n'.join([
            '::' + self.title + '::',
            '@' + self.datetime,
            self.text
        ])