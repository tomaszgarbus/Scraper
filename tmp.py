import urllib.request
from html.parser import HTMLParser


class SportPlScraper(HTMLParser):
    def __init__(self):
        super(SportPlScraper, self).__init__()
        self.home = 'http://www.sport.pl/pilka'

    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            print("Encountered a start tag:", tag, attrs)

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        pass

    def handle_data(self, data):
        super().handle_data(data)
        pass

    def run(self):
        with urllib.request.urlopen(self.home) as response:
            self.html = response.read()
        self.feed(str(self.html))


if __name__ == '__main__':
    scraper = SportPlScraper()
    scraper.run()
    print(scraper.html)
