from wiki_movie.narrators.base_tts import BaseNarrator
from wiki_movie.narrators.engines import dc_tts


def build_narrator(*args, **kwargs):
    return DcttsNarrator(*args, **kwargs)


class DcttsNarrator(BaseNarrator):
    def __init__(self, script, dctts_data_dir, *args, **kwargs):
        h = script[0]['title']
        dc_tts.Hyperparams.test_data = str(dctts_data_dir / 'text_input' / f'{h}.txt')
        dc_tts.Hyperparams.sampledir = str(dctts_data_dir / 'samples' / h)

        dc_tts.process_text_dctts(script, dc_tts.Hyperparams.test_data)

        super().__init__(script)

    def make_narration(self, audio_dir):
        dc_tts.save_samples()
        dc_tts.recombine_wavs(script=self.script,
                              sample_dir=dc_tts.Hyperparams.sampledir,
                              audio_dir=str(audio_dir))
