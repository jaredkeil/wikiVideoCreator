from unittest import TestCase

from wiki_movie.utils import write_seq_to_file, make_directory, file_len, repository_root


class UtilsTest(TestCase):
    def test_repository_root(self):
        found_repo = repository_root.stem
        self.assertEqual(found_repo, 'wikiVideoCreator')

