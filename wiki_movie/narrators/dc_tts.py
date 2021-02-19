from wiki_movie.narrators.base_tts import BaseNarrator
from wiki_movie.narrators.engines import dc_tts as dc_engine


def build_narrator(*args, **kwargs):
    return DcttsNarrator(*args, **kwargs)


class DcttsNarrator(BaseNarrator):
    def __init__(self, script, dctts_data_dir, *args, **kwargs):
        title = script[0]['title']
        dc_engine.Hyperparams.test_data = str(dctts_data_dir / 'text_input' / f'{title}.txt')
        dc_engine.Hyperparams.sampledir = str(dctts_data_dir / 'samples' / title)

        dc_engine.process_text_dctts(script, dc_engine.Hyperparams.test_data)

        super().__init__(script)

    def make_narration(self, audio_dir):
        dc_engine.synthesize()
        dc_engine.recombine_wavs(sample_dir=dc_engine.Hyperparams.sampledir,
                                 audio_dir=str(audio_dir))
