from moviepy.editor import *
import gizeh as gz
from gtts import gTTS
from wiki_scrape import parse_wiki
from skimage.io import imread, imsave
from skimage.transform import resize
from skimage.util import img_as_ubyte
import time
from datetime import datetime


# Default Parameters
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WHITE_GIZEH = (1, 1, 1)
BLACK_GIZEH = (0, 0, 0)

VIDEO_SIZE = (1920, 1080)
IMG_SHAPE = (540, 960)
IMG_DISPLAY_DURATION = 10    #duration, in seconds, to display each image

class WikiMovieMaker():

    def __init__(self, main_keyword):
        self.main_keyword = main_keyword

    def render_text(self, t):
        surface = gz.Surface(1920, 1080, bg_color=BLACK_GIZEH)
        text = gz.text(
            self.title, fontfamily="Helvetica",
            fontsize=120, fontweight='bold', fill=WHITE_GIZEH, xy=(960, 400))
        text.draw(surface)
        return surface.get_npimage()

    def create_paths(self):
        # Directories
        self.IMG_DIR = '../images/' + self.title + "/"
        self.RESIZE_DIR = self.IMG_DIR + "/resize"
        self.AUDIO_DIR = '../audio/'
        self.VID_DIR = '../videos/'
        # Paths
        self.AUDIO_PATH = self.AUDIO_DIR + self.title + ".mp3"
        self.VID_PATH = self.VID_DIR+ self.title + ".mp4"

        for d in [self.IMG_DIR, self.RESIZE_DIR, self.AUDIO_DIR, self.VID_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)

    def text_to_audioclip(self):
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

        for fname in fnames:
            path = os.path.join(self.IMG_DIR, fname)
            img_array = resize(imread(path), output_shape=IMG_SHAPE, mode='constant')
            save_path = os.path.join(self.RESIZE_DIR, fname)
            self.final_img_paths.append(save_path)
            imsave(save_path, img_as_ubyte(img_array))

    def make_movie(self, cutoff=None):

        self.title, self.script = parse_wiki(self.main_keyword)
        if cutoff:
            self.script = self.script[:cutoff]
        self.create_paths()
        # Create TTS (Text-to-Speech) audio
        self.text_to_audioclip()
        # Load and resize images
        self.resize_images()

        # Create Video Clips
        title_text = VideoClip(self.render_text, duration=3)

        image_sequence = ImageSequenceClip(sequence=self.final_img_paths,
                                  durations=self.fixed_durations,
                                  load_images=True).\
                set_position(('center', 400)).\
                fx(vfx.loop, duration=self.DURATION).\
                set_audio(self.audio_clip)

        self.video = concatenate_videoclips([title_text, image_sequence], method='chain').\
                    on_color(color=BLACK, col_opacity=1)
        
        # Encode Video
        start = datetime.now()
        self.video.write_videofile(self.VID_PATH, fps=10, audio_codec="aac")
        dur = datetime.now() - start
        print("Video Encoding completed in time: ", dur)


if __name__ == "__main__":

    WMM = WikiMovieMaker('Badger')
    WMM.make_movie(cutoff=100)