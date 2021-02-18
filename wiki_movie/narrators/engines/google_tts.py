import time

from gtts import gTTS, gTTSError

from wiki_movie.utils import has_extension, add_extension


def save(text, file_name):
    """
    text (str)
    filepath (str)
    """
    if not has_extension(file_name, 'mp3'):
        file_name = add_extension(file_name, 'mp3')

    tts = gTTS(text)
    error_count = 0

    while True:
        try:
            tts.save(file_name)
            print('gTTS success')
            break

        except Exception as e:
            print(e)
            print(f'gTTS save error, trying again. Error count: {error_count}')
            error_count += 1

            # rsp should be <requests.Response>
            if isinstance(e, gTTSError) and e.rsp:
                if e.rsp.status_code == 429:
                    # too many requests, sleep
                    time.sleep(60)
