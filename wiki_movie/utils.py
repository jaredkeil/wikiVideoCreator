from pathlib import Path
import os
import time
import importlib.util
import sys


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
    i = 0
    with open(file_name) as f:
        for _ in f:
            i += 1
    return i  # i will be the index of the last line. 1 is added to account for the folder of resized images.


def localtime_filepath(directory, extension):
    """
    directory -- Path
    extension -- str

    return -- str
    """
    formatted_current_time = time.strftime('%H.%M.%S', time.localtime())
    return str(directory / str(formatted_current_time + '.' + extension))


def has_extension(path, expected_ext):
    root, ext = os.path.splitext(path)
    return ext == '.' + expected_ext


def add_extension(path, suffix):
    return path + '.' + suffix


def change_extension(path, new_extension):
    root, _ = os.path.splitext(path)
    return root + '.' + new_extension


def conditional_import(name):
    if name in sys.modules:
        print(f"{name!r} already in sys.modules")
    elif (spec := importlib.util.find_spec(name)) is not None:
        # If you chose to perform the actual import ...
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        print(f"{name!r} has been imported")
    else:
        print(f"can't find the {name!r} module")


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
