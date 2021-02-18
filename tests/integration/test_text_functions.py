from unittest import TestCase

import wikipediaapi

from wiki_movie.text import generate_script_list, flush_sections, remove_stopwords
from tests.data.wiki_api.flushed_example import flushed


class TextFunctionsTest(TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia('en')

    def test_remove_stopwords(self):
        text = 'this is\n a test[sic] e.g.\tcase.'
        text = remove_stopwords(text)

        self.assertEqual('this is a test case.', text,
                         'Stop word removal incorrect')

    def test_flush_sections(self):
        page = self.wiki.page('Scottish Football League First Division')
        script = generate_script_list(page)

        self.assertListEqual(flushed, script)
