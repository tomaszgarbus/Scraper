from scraper import ArticlesScraper

if __name__ == '__main__':
    scraper = ArticlesScraper(home='http://www.sport.pl/pilka',
                              follow_link=lambda link: link['href'].startswith('http://www.sport.pl/pilka'))
    scraper.run()
