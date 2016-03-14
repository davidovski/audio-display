import argparse
import logging
import sys

import numpy as np
import os
import wavfile
from PIL import Image
from PIL import ImageDraw

__all__ = []
__version__ = 0.1
__date__ = '2015-12-18'
__updated__ = '2016-02-21'
__author__ = 'olivier@pcedev.com'


def write_spectrum(frequencies, spectrum, frame_index, opts):
    bucket_nb = opts.bar_count
    bucket_pixel_spacing = opts.bar_spacing
    bucket_pixel_width = opts.bar_width
    spectrum_len = len(spectrum)
    height = opts.image_height

    image = Image.new("RGBA", (bucket_nb * (bucket_pixel_spacing + bucket_pixel_width), height))
    draw = ImageDraw.Draw(image)

    min_freq = opts.audio_min_freq
    max_freq = opts.audio_max_freq

    display_freq = np.logspace(np.log(min_freq) / np.log(3),
                               np.log(max_freq) / np.log(3),
                               bucket_nb, base=3)

    interpolated_spectrum = np.interp(display_freq, frequencies, spectrum, left=0, right=0)

    for bucket_idx in range(bucket_nb):

        try:
            attenuation = 10 * np.log(interpolated_spectrum[bucket_idx] / spectrum_len)
            line_data = max(height / opts.silence_ceiling * attenuation, -height + 1)
            logging.debug("freq %f, %f dB", display_freq[bucket_idx], attenuation)
        except ValueError:
            # on last frame, we might not have enough data to compute the average in a bucket
            continue

        if line_data:
            bucket_start = bucket_idx * (bucket_pixel_spacing + bucket_pixel_width)
            draw.rectangle((bucket_start, height, bucket_start + bucket_pixel_width, - line_data), fill=(255, 255, 255))

    image.save(opts.output_filename_mask.format(frame_index))

def smooth_spectrum(spectrum, previous_spectrum, alpha=0):
    try:
        return (spectrum + alpha * previous_spectrum) / (1 + alpha)
    except (ValueError, TypeError):
        return spectrum


def compute_frequencies(spectrum, fs):
    return np.arange(spectrum.size) * (fs / 2) / (spectrum.size - 1)


def main(argv=None):
    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.2"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_longdesc = '''Convert audio file to stack of images'''
    program_license = "GPL v3+ 2015 Olivier Jolly"

    if argv is None:
        argv = sys.argv[1:]

    try:
        parser = argparse.ArgumentParser(epilog=program_longdesc,
                                         description=program_license)
        parser.add_argument("-d", "--debug", dest="debug", action="store_true",
                            default=False,
                            help="debug operations [default: %(default)s]")
        parser.add_argument("-n", dest="dry_run", action="store_true",
                            default=False,
                            help="don't perform actions [default: %(default)s]"
                            )
        parser.add_argument("-r", dest="target_fps", default=30, help="input file in wav format")
        parser.add_argument("-v", "--version", action="version", version=program_version_string)

        parser.add_argument("-w", "--bar-width", dest="bar_width", default=50, type=int,
                            help="bar width in output images")
        parser.add_argument("-s", "--bar-spacing", dest="bar_spacing", default=20, type=int,
                            help="bar spacing in output images")
        parser.add_argument("-c", "--bar-count", dest="bar_count", default=15, type=int,
                            help="number of bars in output images")
        parser.add_argument("-b", "--blending", dest="blending", default=0.5, type=float,
                            help="blending of previous spectrum into current one "
                                 "(0 = display only fresh data, 1 = use as many previous than fresh data)")

        parser.add_argument("--image-height", dest="image_height", default=120, type=int, help="output images height")

        parser.add_argument("--audio-min-freq", dest="audio_min_freq", default=50, type=int,
                            help="min frequency in input audio")
        parser.add_argument("--audio-max-freq", dest="audio_max_freq", default=2500, type=int,
                            help="max frequency in input audio")
        parser.add_argument("--audio-gain", dest="audio_gain", default=10, type=int,
                            help="*> linear <* gain in input audio")
        parser.add_argument("--silence-ceiling", dest="silence_ceiling", default=70, type=float,
                            help="opposite of threshold considered silence [in dB, default: %(default)s]")

        parser.add_argument("-i", dest="input_filename", default="input.wav", help="input file in wav format")
        parser.add_argument("-o", dest="output_filename_mask", required=True,
                            help="output filename mask (should contain {:06} or similar to generate sequence)")

        # process options
        opts = parser.parse_args(argv)

    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    if opts.debug:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    # load input file
    fs, data = wavfile.read(opts.input_filename)

    # compute bits per sample
    normalize_bits = 8 * data.dtype.itemsize - 1

    # monoize potential stereo files
    if len(data.shape) > 1:
        raw_data = data.T[0] + data.T[1]
        normalize_bits += 1
    else:
        raw_data = data.T

    # and normalize audio file in the [ -1 ; 1 ] range
    normalized_data = raw_data / 2 ** normalize_bits

    byte_per_frame = fs / opts.target_fps

    frame_start = 0
    frame_index = 0
    previous_spectrum = None

    while frame_start < len(normalized_data):
        # rms = np.sqrt(np.mean(np.square(normalized_data[frame_start: frame_start + 4096])))

        # compute the raw spectrum
        spectrum = abs(np.fft.rfft(normalized_data[frame_start:frame_start + 4096]))

        # smooth it over time
        spectrum = smooth_spectrum(spectrum, previous_spectrum, opts.blending)

        # compute frequencies
        frequencies = compute_frequencies(spectrum, fs)

        # write spectrum to file
        write_spectrum(frequencies, spectrum, frame_index, opts)

        frame_start += byte_per_frame
        frame_index += 1
        previous_spectrum = spectrum

    return 0


if __name__ == "__main__":
    sys.exit(main())
