import pyttsx3
from sys import platform

from wiki_movie.utils import has_extension, add_extension, change_extension


def save(text, file_name):
    """
    text (str)
    file_name (str)
    """
    ext = get_platform_ext()

    if not has_extension(file_name, ext):
        file_name = change_extension(file_name, ext)

    engine = pyttsx3.init()
    engine.save_to_file(text, file_name)
    engine.runAndWait()


def get_platform_ext():
    if platform == 'linux' or platform == 'linux2':
        return 'wav'
    elif platform == 'darwin':
        return 'aiff'
    elif platform == 'win32':
        raise NotImplementedError('pyttsx3 on Windows platform not implemented here.')
    else:
        raise NotImplementedError(f'Unrecognized platform ({platform}) for pyttsx3.')
