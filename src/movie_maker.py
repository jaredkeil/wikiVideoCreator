from moviepy.editor import *
import gizeh as gz
from gtts import gTTS
from skimage.io import imread, imsave
from skimage import transform
from skimage.util import img_as_ubyte
import time
from datetime import datetime

import wikipedia
from image_downloader import master_download


# Default Parameters
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WHITE_GIZEH = (1, 1, 1)
BLACK_GIZEH = (0, 0, 0)

VIDEO_SIZE = (1920, 1080)
IMG_SHAPE = (1080, 1920)
IMG_DISPLAY_DURATION = 5    #duration, in seconds, to display each image

class WikiMovie():

    def __init__(self, page):
        self.page = page
        self.title = self.page.title
        self.script = self.page.content

    def create_paths(self):
        # Directories
        self.IMG_DIR = '../images/' + self.title + "/"
        self.RESIZE_DIR = self.IMG_DIR + "resize/"
        self.AUDIO_DIR = '../audio/'
        self.VID_DIR = '../videos/'
        # Paths
        self.AUDIO_PATH = self.AUDIO_DIR + self.title + ".mp3"
        self.VID_PATH = self.VID_DIR+ self.title + ".mp4"

        for d in [self.IMG_DIR, self.RESIZE_DIR, self.AUDIO_DIR, self.VID_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)
                print(d, "directory created")

    def text_to_audioclip(self):
        print("Converting text to speech. . . ")
        tts = gTTS(self.script, lang='en')
        tts.save(self.AUDIO_PATH)
        self.audio_clip = AudioFileClip(self.AUDIO_PATH)
        self.DURATION = self.audio_clip.duration
        print("Audio Duration: ",
            time.strftime('%H:%M:%S', time.gmtime(self.DURATION)))

    def resize_images(self):
        self.final_img_paths = []

        fnames =  [f for f in os.listdir(self.IMG_DIR) if not (f.startswith('.') or f == 'resize')]
        self.fixed_durations = [IMG_DISPLAY_DURATION for _ in fnames]

        print("Resizing images. . .")
        for fname in fnames:
            path = os.path.join(self.IMG_DIR, fname)
            try:
                img_array = transform.resize(imread(path), output_shape=IMG_SHAPE, mode='constant')[:,:,:3]
            except ValueError:
                continue
            save_path = os.path.join(self.RESIZE_DIR, fname)
            self.final_img_paths.append(save_path)
            imsave(save_path, img_as_ubyte(img_array))

    def make_movie(self, cutoff=None):
        
        print("Video Title: ", self.title)

        if cutoff:
            self.script = self.script[:cutoff]

        self.create_paths()
        # Create TTS (Text-to-Speech) audio
        self.text_to_audioclip()
        # Download and resize images
        master_download(self.title)
        self.resize_images()

        # Create Video Clips
        print("Creating clips. . .")
        title_text = TextClip(self.title, color='white', fontsize=140, size=VIDEO_SIZE,
                                method='caption').set_duration(2)

        thanks = TextClip("Thanks for watching \n and listening",
                            color='white', fontsize=72, size=VIDEO_SIZE, method='caption').\
                            set_duration(2)

        subscribe = TextClip("Please Subscribe!",
                                color='white', fontsize=72, size=VIDEO_SIZE, method='caption').\
                                set_duration(2)

        image_sequence = ImageSequenceClip(sequence=self.final_img_paths,
                                  durations=self.fixed_durations,
                                  load_images=True).\
                set_position(('center', 400)).\
                fx(vfx.loop, duration=self.DURATION).\
                set_audio(self.audio_clip)

        self.video = concatenate_videoclips([title_text, image_sequence, thanks, subscribe],
                                            method='compose').\
                                            on_color(color=BLACK, col_opacity=1)
        # Encode Video
        start = datetime.now()
        self.video.write_videofile(self.VID_PATH, fps=0.5, codec='mpeg4', audio_codec="aac")
        dur = datetime.now() - start
        print("Video Encoding completed in time: ", dur)

        self.audio_clip.close()
        title_text.close()
        thanks.close()
        subscribe.close()

if __name__ == "__main__":
    page = wikipedia.page('Badger')
    WMM = WikiMovie(page)
    WMM.make_movie(cutoff=300)