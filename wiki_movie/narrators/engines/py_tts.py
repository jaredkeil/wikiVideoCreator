import pyttsx3

from wiki_movie.utils import has_extension, change_extension, \
    get_platform_audio_ext


def save(text, file_name):
    """
    text (str)
    file_name (str)
    """
    ext = get_platform_audio_ext()

    if not has_extension(file_name, ext):
        file_name = change_extension(file_name, ext)

    engine = pyttsx3.init()
    engine.save_to_file(text, file_name)
    engine.runAndWait()
