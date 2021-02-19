from wiki_movie.utils import make_directory


class BaseNarrator:
    def __init__(self, script):
        """
        script (list) -- list of script dictionaries (as used in WikiMovie class)
        """
        self.script = script

    def make_narration(self, audio_dir):
        make_directory(audio_dir)
        for script_section in self.script:
            self._narrate_section(script_section, audio_dir)

    def _narrate_section(self, section, audio_dir):
        section_audio_file_prefix = audio_dir / section['title']

        self._save_section(section['title'], audio_dir / (section['title']+'_header'))
        if section['text']:
            self._save_section(section['text'], audio_dir / (section['title']+'_text'))

    def _save_section(self, *args, **kwargs):
        pass
