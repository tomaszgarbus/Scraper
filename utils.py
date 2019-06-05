import validators


def is_link_relative(link: str) -> bool:
    """
    A heuristic determining whether a link is relative.

    :param link: Either a URL or a relative link.
    :return: True if the link has been determined to be relative.
    """
    return not validators.url(link)
