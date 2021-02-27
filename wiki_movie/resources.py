import pandas as pd
from wikipediaapi import Wikipedia

W_API = Wikipedia('en')


def wiki_page_list(url, n_pages=None, article_column='Article'):
    tables = pd.read_html(url)
    for table in tables:
        if article_column in table:
            break
    if n_pages is None:
        n_pages = table.shape[0]
    return list(table[article_column][:n_pages])


def top25():
    return wiki_page_list("https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report", 25)
