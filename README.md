## Video Creater From Wikipedia


### Installation:

Install Selenium, geckodriver, firefox:
 - etc...

Install [ImageMagick](https://imagemagick.org/script/download.php), and [Ghostscript](https://www.ghostscript.com/doc/9.53.3/Install.htm)
    
- method depends on operating system (Linux, macOS, Windows)

Install [SoundFile](https://pysoundfile.readthedocs.io/en/latest/#installation)
   
- Linux: `sudo apt-get install libsndfile1-dev`
- MacOS, Windows: `pip install soundfile`

*Recommended: Create and activate a virtual environment before next steps[python venv, conda, pipenv].*

Install python dependencies

    pip install -r requirements

Optional: Install PyGame, if wanting to run inline previews in notebooks

    pip install pygame

Notes:
 - Python above 3.7.6 is unstable
 - First run of `create.py` may prompt for a key-code.