from pathlib import Path
import os
from moviepy.editor import *
import gizeh as gz
from gtts import gTTS
from skimage.io import imread, imsave
from skimage import transform
from skimage.util import img_as_ubyte
import time
from datetime import datetime

import wikipediaapi
from image_downloader import master_download
from im_funcs import maxsize_pad


# Default Parameters
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WHITE_GIZEH = (1, 1, 1)
BLACK_GIZEH = (0, 0, 0)

VIDEO_SIZE = (1920, 1080)
IMG_SHAPE = (1080, 1920)
IMG_DISPLAY_DURATION = 4    #duration, in seconds, to display each image

excluded_sections = {'See also', 'References', 'Further reading', 'External links',
                'Formats and track listings', 'Credits and personnel', 'Charts',
                'Certifications', 'Release history'}

stops = {'\n', '\t', 'e.g.', '[sic]', '[...]', 'i.e.',}


class WikiMovie():
    """
    Make movies in standard format (.mp4) from wikipedia pages.
    Initialize with 'page' object from wikipedia Python module.
    Primary user function is make_movie().
    """
    def __init__(self, page, narrator='gtts', overwrite=True):
        self.page = page
        self.title = self.page._attributes['title']
        self.narrator = narrator
        self.overwrite = overwrite
        self.script = [{'title': page.title, 
                        'level': 0, 
                        'text': self.clean_text(page.summary)}]
        self.keywords = [' ']
        self.cliplist = []
        
        self.p = Path(__file__).resolve().parents[0]
        # self.p = Path(os.path.abspath('')).resolve() ## For jupyter notebook
        self._imgidx = 0 # For starting image seqeunces on unique image
        self.cutoff = None
        

    def create_paths(self):
        # Image directories
        self.parent_images = self.p / 'images'
        self.imgdir = self.p / 'images'/ self.title
#         self.resizedir = self.imgdir / 'resize'
        # audio directories
        self.parent_audio = self.p / 'audio'
        self.auddir = self.p / 'audio' / self.title
        # dc_tts directory
        self.dctts_dir = self.p / 'dc_tts'
        self.dctts_in = self.dctts_dir / 'text_input'
        self.dctts_out = self.dctts_dir / 'samples' / self.title
        # URL lists text files directory
        self.url_dir = self.p / 'url_files'
        # Video directory (all article videos stored in folder, files named by title)
        self.viddir = self.p / 'videos'
        # Video save path
        self.vidpath = self.viddir / (self.title + ".mp4")

        print('creating paths...')
        for d in [self.imgdir, self.parent_audio, self.auddir, self.dctts_dir,\
                self.dctts_in, self.dctts_out, self.url_dir, self.viddir]:
            if not d.exists():
                d.mkdir()
                print(d, "directory created")
            elif d.exists():
                print(d, "exists")

    def resize_images(self, sd):
        sd['imgpaths'] = [] #image paths
        sk_imgdir = self.imgdir / sd['title'] # supplemented keyword used earlier by image search/download
        contents = sk_imgdir.glob('*') 
        fnames =  [x for x in contents if x.is_file() and x.parts[-1][0] != '.']
        n_imgs = len(fnames)
        sd['idd'] = [IMG_DISPLAY_DURATION for _ in fnames]
        
        resizedir = sk_imgdir / 'resize'
        if not resizedir.exists():
            resizedir.mkdir()
            print(f'made directory {resizedir}')
        
        for i, fname in enumerate(fnames, start=1):
            sys.stdout.write(f"Resizing Images [{'#'*(i) + ' '*(n_imgs - si)}]   \r")
            sys.stdout.flush()
            
            path = str(sk_imgdir / fname)
            print(path)
            save_path = str(resizedir / fname)
            print(resizedir)
            print(save_path)
            try:
                maxsize_pad(path, save_path)
            except Exception:
                continue
            sd['imgpaths'].append(save_path)

                             
    def process_images(self):
        for sd in self.script:
            if sd['title'] in self.keywords:
                self.resize_images(sd)
    

    def google_tts(self, string, mp3path):
        tts = gTTS(string)
        tts.save(mp3path)
                        
    
    def make_narration(self):
        if self.narrator == 'dctts':
            #check if narration already exists
            if len(os.listdir(self.dctts_out)) > 0 and self.overwrite == False:
                print('Not going to make narration')
            else:
                dctts_synthesize()
                self.combine_wavs()
        else:
            for sd in self.script:
                prefix = str(self.auddir / sd['title'])
                self.google_tts(string=sd['title'], 
                                mp3path=prefix + '_header.mp3')
                if sd['text']:
                    self.google_tts(string=sd['text'],
                                   mp3path=prefix + '_text.mp3')

                             
    def clean_text(self, text):
        """
        Remove stop words
        """
        for x in stops:
            text = text.replace(x, '')
        return text

    def flush_sections(self, sections, level=0):
        """
        Get text from all levels (sections, subsections) in page order and generate narrations
        """
        for s in sections:
            if s.title in excluded_sections:
                print('exluding', s.title)
                continue
            else:
                self.script.append({'title':s.title, 
                                    'level': level+1, 
                                    'text': self.clean_text(s.text)})
                # recursion to next level. Once lowest level is reached, next main section will be accessed
                self.flush_sections(s.sections, level+1)
    
                             
    def get_keywords(self):
        self.keywords += [sd['title'] for sd in self.script[1:] if sd['text']]


    def output_text(self):
        """
        Process page text for DC_TTS creation. Write to file. 
        """
        self.sent_path = self.dctts_in / f"{self.title}.txt"
        hp.test_data = self.sent_path
        
        with self.sent_path.open('w') as sf:
            sf.write(f"Script for Wikipedia article {self.title}\n")
            # Section by section
            # sd = section_dict
            for sd in self.script:
                # d = {'title': section title, 'level': level, 'text': section text}
                # Full length sentences, possibly greater than max number of characters for model
                full_sents = [sd['title']] + sd['text'].split('.')
                # break section down into max 180 character chunks 
                sents = []
                for sent in (full_sents):
                    sent = sent.strip()
                    if not sent:
                        continue
                    if len(sent) > hp.max_N:
                        split_on = sent[:hp.max_N].rfind(" ")
                        tmp_split = [sent[:split_on], sent[split_on:]]
                        while len(tmp_split[-1]) > hp.max_N:
                            last = tmp_split.pop()
                            split_on = last[:hp.max_N].rfind(" ")
                            tmp_split += [last[:split_on], last[split_on:]]
                        sents.extend(tmp_split)     
                    else:
                        sents.append(sent)         
                sd['n_segments'] = len(sents)    
                for i, sent in enumerate(sents): 
                    sf.write(f"{sd['title']}:{i} {sent}\n")
    
                             
    def combine_wavs(self):
        """For use with dctts synthesize"""
        ct = 1
        for sd in self.script:
            # convert title speech to mp3
            AS_title = AudioSegment.from_wav(str(self.dctts_out / (str(ct) + '.wav')))
            path = str(self.auddir / (sd['title'] + '_header.mp3'))
            AS_title.export(path, format='mp3')
            # combine rest of speech, convert to mp3                               
            n = sd['n_segments']
            AS_text = sum([AudioSegment.from_wav(str(self.dctts_out / (str(i) + '.wav'))) 
                           for i in range(ct + 1, ct + n)])
            path = str(self.auddir / (sd['title'] + '_text.mp3'))
            AS_text.export(path, format='mp3')
            ct += n
             
                             
    def create_clip(self, section):
        """
        Load back audio and attach it to proper clip
        Args: 
            section (dict): A dictionary as found in self.script
        Returns:
            V (VideoClip): Combined TextClip and (optional) ImageSequence
        """
        prefix = str(self.auddir / section['title'])
        ACH = AudioFileClip(prefix + '_header.mp3')
                  
        fontsize = 130 - (30 * section['level']) # higher level means deeper 'indentation'
        V = TextClip(section['title'], color='white', fontsize=fontsize, 
                    size=VIDEO_SIZE, method='caption').\
                    set_audio(ACH).set_duration(ACH.duration)
                             
        if section['text']:
            ACT = AudioFileClip(prefix + '_text.mp3')
                             
            # self._imgidx += 1             
            IS = ImageSequenceClip(sequence=section['imgpaths'],
                                durations=section['idd'], load_images=True).\
                            set_position(('center', 400)).\
                            fx(vfx.loop, duration=ACT.duration).\
                            set_audio(ACT)
            V = concatenate_videoclips([V, IS])
    
        return V

                             
    def make_movie(self, hp, cutoff=None):
        """
        Args:
            cutoff (int): Limit the length of the script. Used like script[:cutoff]
        Returns:
            None
        """
        print("Video Title: ", self.title)
        self.cutoff = cutoff
        self.create_paths()
        
        self.flush_sections()
        
        self.output_text()
        hp.test_data = str(WMM.sent_path)
        hp.sampledir = str(WMM.dctts_out) 
        # Download and resize images
        self.get_keywords()
        master_download(main_keyword=self.title, supplemented_keywords=self.keywords,
                        url_dir=self.url_dir, img_dir=self.imgdir, num_requested=20)
        self.resize_images()
        print('\n') 
        
        self.make_narration()                
        # Create Video Clips
        print("Creating clips. . .")
        for sd in self.script:
            self.create_clip(sd)

                             
        thanks = TextClip("Thanks for watching \n and listening",
                            color='white', fontsize=72, size=VIDEO_SIZE, method='caption').\
                            set_duration(2)

        subscribe = TextClip("Please Subscribe!",
                                color='white', fontsize=72, size=VIDEO_SIZE, method='caption').\
                                set_duration(2)

        self.video = concatenate_videoclips(self.cliplist + [thanks, subscribe],
                                            method='compose').\
                                            on_color(color=BLACK, col_opacity=1)
        # Encode Video
        start = datetime.now()
        self.video.write_videofile(str(self.vidpath) , fps=1, codec='mpeg4', 
                                   audio_codec="aac", preset='ultrafast')
        dur = datetime.now() - start
        print("Video Encoding completed in time: ", dur)

        # self.audio_clip.close()
        # title_text.close()
        thanks.close()
        subscribe.close()
        self.video.close()
        

if __name__ == "__main__":
    wiki = wikipediaapi.Wikipedia('en')
    page = wiki.page(input("What would you like the video to be about? "))
    WMM = WikiMovie(page, narrator='gtts')
    WMM.make_movie(cutoff=None)
