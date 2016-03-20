audio-display
=============

**audio-display** is a set of utility aimed at rendering images based on audio input.
It aims at generating images to produce visual "companion" to audio files. Typically to create
a video clip supporting a musical composition.


fft2png
-------

**fft2png** is a command line utility to create a set of image files representing audio spectrum from a wav file.
It is an offline version of a spectrum analyser output and is not totally dissimilar to `Sonic Candle`_.

Generated files can be imported and postprocessed in any video edition tool accepting a set of images as input.
Just make sure that the framerate used during the call to **fft2png** matches the framerate at which you consume
images in your video edition software. Libre software able to consume and use those images includes, but aren't
limited to, Natron_.

You can also use FFmpeg_ for either previewing quickly or for simple needs (just the spectrum over a fixed image
or a video. Some samples of `ffmpeg usage`_ can be found later.


Usage
.....

    usage: fft2png [-h] [-d] [-n] [-r TARGET_FPS] [-R {0,1,2,3}] [-v]
                   [-w BAR_WIDTH] [-s BAR_SPACING] [-c BAR_COUNT] [-C COLOR]
                   [-b BLENDING] [-W FFT_WINDOW] [--image-height IMAGE_HEIGHT]
                   [--audio-min-freq AUDIO_MIN_FREQ]
                   [--audio-max-freq AUDIO_MAX_FREQ]
                   [--silence-ceiling SILENCE_CEILING] [-i INPUT_FILENAME] -o
                   OUTPUT_FILENAME_MASK

    GPL v3+ 2015 Olivier Jolly

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           debug operations [default: False]
      -n                    don't perform actions [default: False]
      -r TARGET_FPS, --framerate TARGET_FPS
                            output framerate [default: 30]

      -R {0,1,2,3}, --renderer {0,1,2,3}
                            which renderer to use to display bars (0=filled, 1=hollow, 2=symetrical filled, 3=symetrical hollow)

      -v, --version         show program's version number and exit
      -w BAR_WIDTH, --bar-width BAR_WIDTH
                            bar width in output images
      -s BAR_SPACING, --bar-spacing BAR_SPACING
                            bar spacing in output images
      -c BAR_COUNT, --bar-count BAR_COUNT
                            number of bars in output images
      -C COLOR, --color COLOR
                            hexa color of bars [RRGGBB or RRGGBBAA, default: FFFFFFFF]
      -b BLENDING, --blending BLENDING
                            blending of previous spectrum into current one (0 =
                            display only fresh data, 1 = use as many previous than
                            fresh data)
      -W FFT_WINDOW, --window FFT_WINDOW
                            window size for FFT [default: 4096]
      --image-height IMAGE_HEIGHT
                            output images height
      --audio-min-freq AUDIO_MIN_FREQ
                            min frequency in input audio
      --audio-max-freq AUDIO_MAX_FREQ
                            max frequency in input audio
      --silence-ceiling SILENCE_CEILING
                            opposite of threshold considered silence [in dB,
                            default: 70]
      -i INPUT_FILENAME     input file in wav format
      -o OUTPUT_FILENAME_MASK
                            output filename mask (should contain {:06} or similar
                            to generate sequence)

    Convert audio file to stack of images

**-r**
  Framerate of the generated images. Should match the framerate at which they will be consumed.
  Higher framerate gives a smoother result.

**-R**
  Aspect of the bar representing power for one frequency. 0 uses filled boxes, 1 uses hollow boxes,
  2 uses filled boxes vertically centered and 3 uses hollow boxes vertically centered.

**-w**
  Width (in pixel) per bar.

**-s**
  Spacing (in pixel) between bars.

**-c**
  Number of bars per images.

**-C**
  Color of the bars in hexa. Can be RGB or RGBA. For instance, FF0000 will render pure opaque red bars,
  00FF0080 will render 50% transparent pure green bars, ...

**-b**
  Blending ratio from previous frame into current one. When set to 0, only fresh data will be used to
  render bars. When set to 1, bars will be rendered from an average of the fresh and previous frame data.
  Intermediate values will inject a fraction of the previous frame data into the current one for rendering.
  Lower values tends to render more reactive spectrum while higher ones will smooth data over time and react slower.

**-W**
  Spectrum generation window is the amount of data in the audio file used to determine the spectrum raw data.
  Lower value will make spectrum blockier but will be slightly faster to generate.

****

FFMpeg usage
............

.. _ffmpeg usage:

Installation
------------

**audio-display** will be installable from PyPI with a single pip command::

    pip install audio-display

Alternatively, **audio-display** can be run directly from sources after a git pull (recommended if you want to tweak
or read the source)::

    git clone https://gitlab.com/zeograd/audio-display.git
    cd audio-display && python setup.py install

or directly from its git repository::

    pip install git+https://gitlab.com/zeograd/audio-display.git

.. _Sonic Candle: http://soniccandle.sourceforge.net/
.. _Natron: http://natron.fr
.. _FFmpeg: http://ffmpeg.org
