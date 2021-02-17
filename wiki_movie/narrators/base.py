class BaseNarrator:
    def __init__(self, script):
        """
        title (str) -- title of script
        script (list) -- list of script dictionaries as used in WikiMovie class
        """
        self.title = script[0]['title']
        self.script = script

    def make_narration(self, audio_dir):
        for script_section in self.script:
            self._narrate_section(script_section, audio_dir)

    def _narrate_section(self, section, audio_dir):
        section_audio_file_prefix = audio_dir / section['title']

        self._save_section(section['title'], section_audio_file_prefix.with_suffix('_header'))
        if section['text']:
            self._save_section(section['text'], section_audio_file_prefix.with_suffix('_text'))

    def _save_section(self, *args, **kwargs):
        pass
