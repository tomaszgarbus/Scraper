from sportpl_scraper import SportPlArticlesScraper, sportpl_follow_link

if __name__ == '__main__':
    scraper = SportPlArticlesScraper(home='http://www.sport.pl/pilka',
                                     domain='http://www.sport.pl',
                                     follow_link=sportpl_follow_link)
    scraper.run()
