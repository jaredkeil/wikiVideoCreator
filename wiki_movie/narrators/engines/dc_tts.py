import os

from pydub import AudioSegment

from wiki_movie.dc_tts.synthesize import synthesize
from wiki_movie.dc_tts.hyperparams import Hyperparams


def recombine_wavs(script, sample_dir, audio_dir):
    """
    Combine the short wav files outputs from dc-tts into by article section.

    script (list)
    sample_dir (str) -- original location of the split up files
    audio_dir (str) -- destination for out_paths of combined files
    """
    # ct used in .wav filenames, e.g. '1.wav', '2.wav', '3.wav', etc.
    ct = 1
    for sd in script:
        name = sd['title']
        n = sd['n_segments']

        AudioSegment.from_wav(
            os.path.join(sample_dir, f'{ct}.wav')
        ).export(out_f=os.path.join(audio_dir, f'{name}_header.mp3'), format='mp3', codec='libmp3lame')

        if sd['text'] or sd['level'] == 0:
            audio_seg = AudioSegment.from_wav(os.path.join(sample_dir, f'{ct+1}.wav'))

            for i in range(ct + 2, ct + n):
                audio_seg += AudioSegment.from_wav(os.path.join(sample_dir, f'{i}.wav'))

            audio_seg.export(out_f=os.path.join(audio_dir, f'{name}_text.mp3'), format='mp3', codec='libmp3lame')
        ct += n


def process_text_dctts(script, file_path):
    """
    Process article text into lines within pre-defined character limit of DC_TTS model.

    Params:
        script (list) -- list of section dictionaries
        file_path (str) -- output path of .txt file
    """

    with open(file_path, 'w') as sf:
        sf.write(f"Script for Wikipedia article {script[0]['title']}\n")
        for section in script:
            s_chunks = chunk_script_section(sd=section, n=Hyperparams.max_N)
            section['n_segments'] = len(s_chunks)  # used in re-combining wav files later
            section_title = section['title'].replace(' ', '')
            for i, sentence in enumerate(s_chunks):
                sf.write(f"{section_title}:{i} {sentence}\n")


def chunk_script_section(sd, n):
    """
    Split simply on period. Problematic for titles like Dr. and abbreviations like D.M.Z.

    Params:
        sd (dict) -- {'title': section title (str), 'level': level (int), 'text': section text (str)}
        n (int) -- chunk size
    Returns:
        chunks (list) -- list of sentence strings
    """

    original_sentences = [sd['title']] + sd['text'].split('.')

    chunks = []

    for sent in original_sentences:
        sent = sent.strip()
        if not sent:
            continue

        if len(sent) > n:
            split_on = sent[:n].rfind(" ")
            tmp_split = [sent[:split_on], sent[split_on:]]

            while len(tmp_split[-1]) > n:
                last = tmp_split.pop()
                split_on = last[:n].rfind(" ")
                tmp_split += [last[:split_on], last[split_on:]]
            chunks.extend(tmp_split)

        else:
            chunks.append(sent)

    return chunks
