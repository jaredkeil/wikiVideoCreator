

STOPS = {'\n', '\t', 'e.g.', '[sic]', '[...]', 'i.e.', }  # strings to remove from article text


def remove_stops(text):
    """
    Remove stop words
    """
    for x in STOPS:
        text = text.replace(x, '')
    return text