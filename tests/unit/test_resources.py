from unittest import TestCase

from wiki_movie import resources


class ResourcesTest(TestCase):
    def test_wiki_page_list(self):
        url = "https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report/February_7_to_13,_2021"
        page_list = resources.wiki_page_list(url, 25)
        print(page_list)
        self.assertEqual(25, len(page_list), 'Page list function did correct number of pages')

    def test_wiki_page_list_with_length_limit(self):
        url = "https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report/February_7_to_13,_2021"
        page_list = resources.wiki_page_list(url, 10)
        self.assertEqual(10, len(page_list), 'Page list function did correct number of pages')

    def test_wiki_page_list_with_zero(self):
        url = "https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report/February_7_to_13,_2021"
        page_list = resources.wiki_page_list(url, 0)
        self.assertListEqual([], page_list, 'Page list function did correct number of pages')

    def test_wiki_page_list_no_n_pages(self):
        url = "https://en.wikipedia.org/wiki/List_of_World_Heritage_in_Danger"
        page_list = resources.wiki_page_list(url, article_column='Name')
        print(page_list)
        self.assertEqual(53, len(page_list))

    def test_top25(self):
        top25_list = resources.top25()
        print(top25_list)
        print(type(top25_list))
        self.assertEqual(25, len(top25_list), 'Top 25 list did not contain 25 articles')
