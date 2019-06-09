class ScraperConfig:
    def __init__(self):
        pass

    def state_cache_fname(self) -> str:
        """
        Filename to the ScraperState cache. it will be placed in `cache` folder.
        :return: Filename to the state cache.
        """
        raise NotImplementedError()

    def follow_link(self, link: str) -> bool:
        """
        Given a link, determines whether scraper should queue it for visit.

        :param link: An absolute URL.
        :return: A boolean
        """
        raise NotImplementedError()
