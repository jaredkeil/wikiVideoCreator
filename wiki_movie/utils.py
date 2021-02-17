from pathlib import Path
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
