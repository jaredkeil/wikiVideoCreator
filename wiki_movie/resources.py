import pandas as pd
from wikipediaapi import Wikipedia

W_API = Wikipedia('en')


def wiki_page_list(url, n_pages=None, article_column='Article'):
    tables = pd.read_html(url)
    selected_table = None
    for table in tables:
        if article_column in table:
            selected_table = table
            break
    if selected_table is None:
        raise KeyError(f'No column "{article_column}" found in any tables at {url}.')

    if n_pages is None:
        n_pages = selected_table.shape[0]
    return list(selected_table[article_column][:n_pages])


def top25():
    return wiki_page_list("https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report", 25)
