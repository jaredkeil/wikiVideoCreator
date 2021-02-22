[![Build Status](https://www.travis-ci.com/jaredkeil/wikiVideoCreator.svg?branch=master)](https://www.travis-ci.com/jaredkeil/wikiVideoCreator)

# create videos from Wikipedia articles

Turn Wikipedia articles into videos with computer-generated overdubbing, and the option to upload directly to YouTube.
Includes helpful parsers for Wikipedia API requests, as well as a module for downloading pictures from Google image searches.

## Installation:

### Firefox, geckodriver:

`sudo apt install firefox`

`sudo apt-get install firefox-geckodriver`

Or use homebrew.

`brew install --cask firefox'
`brew install geckodriver`

(Selenium installs with python dependencies in requirements.txt)


### [ImageMagick](https://imagemagick.org/script/download.php), and [Ghostscript](https://www.ghostscript.com/doc/9.53.3/Install.htm):
    

  `sudo apt install imagemagick` or `brew install imagemagick`

  Note, because of issue with MoviePy, you may need to alter the policy.xml file of ImageMagick (see [this issue](https://github.com/Zulko/moviepy/issues/401#issuecomment-278679961)). To find where the file is located, run:
  
  `convert -list policy`

  The top line of the output should look like
  `Path: /etc/ImageMagick-6/policy.xml`

  If instead it is `Path: [built-in]`, then no changes may be necessary.
  
  Edit line 88, or whichever line the policy refers to the "path" domain, to allow rights for read and write.
  
  `sudo nano /etc/ImageMagick-6/policy.xml`

  Original:
  
  `<policy domain="path" rights="none" pattern="@*"/>`

  Change:

  `<policy domain="path" rights="read | write" pattern="@*"/>`

- Ghostscript:

    `sudo apt install ghostscript` or `brew install ghostscript`

### [SoundFile](https://pysoundfile.readthedocs.io/en/latest/#installation)
   
- Linux: `sudo apt-get install libsndfile1-dev`
- MacOS, Windows: `pip install soundfile`


### Python dependencies
*Recommended: Create and activate a virtual environment before next steps[python venv, conda, pipenv].*

`pipenv install` (recommended) or `pip install -r requirements.txt`

Optional: Install PyGame, if wanting to run inline previews in notebooks

`pip install pygame`

## Usage

### Running with python

    python run.py -s [Article Title] -n  [narrator name] -o

Before running, you must obtain a client_secrets.json file for the YouTube API, and store it in the wiki_movie directory.


Example

    python run.py -s Boston -n py_tts -o

Required arguments:

    -s --single_page      Title of the article to process

Options arguments:

| Parameter                 | Default       | Description   |
| :------------------------ |:-------------:| :-------------|
| -n --narrator   |  sys_tts  | Speech generation engine. Accepted values: py_tts, google_tts, dc_tts |
| -o --overwrite  | True      | Flag, which if set, will overwrite any data of an article of the same name |


 - The first run of `run.py` may prompt on the terminal for a key-code, which will be available in a browser window.

### Narrators

- sys_tts: Automatically uses the OS built-in speech command
  - MacOSX: NSSS
  - Linux: espeak
  - Windows: not implemented
- py_tts: Uses pyttsx3
- google_tts: Uses gTTS
- dc_tts: Deep Convolutional TTS

