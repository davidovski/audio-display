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
