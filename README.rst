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

Example
.......

To use default values when generating spectrum, just invoke::

    fft2png -i input.wav -o output-{:06}.png

`result of default fft2png settings`_

For a slightly different result, you can invoke it like this::

    fft2png -R2 -w4 -s4 -c30 -C FF8080A0 --audio-min-freq 100 -i input.wav -o output-{:06}.png

You'll end up with 30 symetrical transparent redish solid bars 4 pixels wide, spaced by 4 pixels

`result of red solid symetrical bars ff2png settings`_

****

FFMpeg usage
............

.. _ffmpeg usage:

If you already have a video as background and want to add spectrogram center on it while adding some musique, you can
invoke ffmpeg like this::

    ffmpeg -i <background_video.mp4> -framerate <generated frames framerate> -i <audio-00%4d.png> -filter_complex "overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:shortest=1" -i <music.wav> -map 2:0 -vframes <number of generated frames> -strict -2 <output.mp4> -y

where :
  * <background_video.mp4> is the filename of your background video
  * <generated frames framerate> is the framerate used when generating spectrogram frames
  * <audio-00%4d.png> is the mask of the generated frames to overlay
  * <music.wav> is the filename of the your music
  * <number of generated frames> is, well, the number of generated spectrogram frames
  * <output.mp4> is the generated muxed video

A few notes :
  * you can change the overlay position by setting the position in absolute coordinates or using some maths with main_w, main_h, overlay_w, overlay_h as show here
  * **-y** is for overwriting the result file
  * **-strict -2** alleviates some error with aac encoding on my version/system combo
  * the background video will not loop. As for now (ffmpeg 3.0.1), looping is not for video. If your video is too short, prepare one which is long enough by concatenating it several times. The **shortest=1** in the filter expression will  stop whenever an input stream (background video, spectrogram images or music) reaches its end.
  * use the ffmpeg manual, Luke

If you want to use a static image as background, the invocation becomes something like::

    ffmpeg -loop 1 -i <background_image.jpg> -framerate <generated frames framerate> -i <audio-00%4d.png> -filter_complex "overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:shortest=1" -i <music.wav> -map 2:0 -vframes <number of generated frames> -strict -2 <output.mp4> -y

The main difference being the **-loop 1** to loop the background image over and over until one of the other
stream ends.

Installation
------------

**audio-display** is installable from PyPI with a single pip command::

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
.. _result of default fft2png settings: https://i.imgur.com/hrc0YRv
.. _result of red solid symetrical bars ff2png settings: https://imgur.com/e0hy5qG
