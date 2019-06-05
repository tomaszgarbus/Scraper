from scraper import ArticlesScraper

if __name__ == '__main__':
    follow_link = lambda link: link['href'].startswith('http://www.sport.pl/pilka') or link['href'].startswith('/pilka')
    scraper = ArticlesScraper(home='http://www.sport.pl/pilka',
                              domain='http://www.sport.pl',
                              follow_link=follow_link)
    scraper.run()
