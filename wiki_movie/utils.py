import os
from pathlib import Path
import shutil
import sys
import time


repository_root = Path(__file__).resolve().parents[1]


def write_seq_to_file(seq, file_path):
    """
    seq -- iterable
    file_path -- Path object
    """
    with file_path.open('w') as wf:
        for item in seq:
            wf.write(item + '\n')


def make_directory(directory):
    """
    directory -- Path object
    """
    if directory.exists():
        print(directory, "exists")
    else:
        directory.mkdir(parents=True)
        print(directory, "directory created")


def file_len(file_name):
    """
    Returns number of lines in text-like file_name
    """
    i = 0
    with open(file_name) as f:
        for _ in f:
            i += 1
    return i


def localtime_filepath(directory, extension):
    """
    Generates a filepath of current local time, with given extension.

    directory -- Path
    extension -- str

    Returns -- str
    """
    formatted_current_time = time.strftime('%H.%M.%S', time.localtime())
    return str(directory / str(formatted_current_time + '.' + extension))


def has_extension(path, expected_ext):
    """
    Check if file has extension. <expected_ext> should not include a dot ('.')
    path (str or Path) -- e.g. '/path/to/file.ext'
    expected_ext (str) -- e.g. 'wav'

    Returns
    has_extension (bool)
    """
    root, ext = os.path.splitext(path)
    return ext == '.' + expected_ext


def add_extension(path, suffix):
    """
    Returns path + '.' + suffix
    """
    return path + '.' + suffix


def change_extension(path, new_extension):
    root, _ = os.path.splitext(path)
    return root + '.' + new_extension


def rm_directory(directory):
    # Remove directory and all it's contents, including sub-directories and files
    try:
        shutil.rmtree(directory)
    except FileNotFoundError:
        print(f'Tried deleting {directory}, but was not found.')


def rm_file(file_path):
    # Delete file if path is found. Does not raise error if path not found
    if file_path.exists():
        file_path.unlink()


def get_platform_audio_ext():
    """
    Return default extension (str) for included platform audio encoders. Does not include '.'
    """
    if sys.platform == 'darwin':
        return 'aiff'

    elif sys.platform in ('linux', 'linux2', 'win32'):
        return 'wav'
    else:
        raise NotImplementedError(f'Platform "{sys.platform}" unrecognized. Cannot find default audio file extension')
