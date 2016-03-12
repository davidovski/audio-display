import argparse
import logging
import sys

import numpy as np
import os
import wavfile
from PIL import Image

__all__ = []
__version__ = 0.1
__date__ = '2015-12-18'
__updated__ = '2016-02-21'
__author__ = 'olivier@pcedev.com'


def write_spectrum(spectrum, frame_index, fs, opts):
    bucket_nb = opts.bar_count
    bucket_pixel_spacing = opts.bar_spacing
    bucket_pixel_width = opts.bar_width
    half_len = int(len(spectrum))
    height = opts.image_height
    im_data = np.zeros((height, bucket_nb * (bucket_pixel_spacing + bucket_pixel_width)), dtype=np.uint8)

    min_freq = opts.audio_min_freq
    max_freq = opts.audio_max_freq

    log_buckets = np.append(  # np.ones(1),
        (np.logspace(np.log(min_freq / (fs / 2 / half_len)) / np.log(3),
                     np.log(max_freq / (fs / 2 / half_len)) / np.log(3),
                     bucket_nb, base=3)).astype('int'),
        np.array([half_len]))

    for bucket in range(bucket_nb):
        try:
            if log_buckets[bucket] >= log_buckets[bucket + 1]:
                log_buckets[bucket + 1] = log_buckets[bucket] + 1
        except KeyError:
            pass

    gain = opts.audio_gain

    for bucket_idx in range(bucket_nb):

        try:
            line_data = int(
                gain * 20 * np.average(spectrum[log_buckets[bucket_idx]:log_buckets[bucket_idx + 1]]) / half_len)
        except ValueError:
            # on last frame, we might not have enough data to compute the average in a bucket
            continue

        if line_data:
            bucket_start = bucket_idx * (bucket_pixel_spacing + bucket_pixel_width)
            im_data[-line_data:, bucket_start:bucket_start + bucket_pixel_width] = 255

    Image.fromarray(im_data).save(opts.output_filename_mask.format(frame_index))


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

        parser.add_argument("--image-height", dest="image_height", default=120, type=int, help="output images height")

        parser.add_argument("--audio-min-freq", dest="audio_min_freq", default=50, type=int,
                            help="min frequency in input audio")
        parser.add_argument("--audio-max-freq", dest="audio_max_freq", default=2500, type=int,
                            help="max frequency in input audio")
        parser.add_argument("--audio-gain", dest="audio_gain", default=10, type=int,
                            help="*> linear <* gain in input audio")

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
        raw_data = data.T[0] + data.T[1]  # this is a two channel soundtrack, I get the first track
        normalize_bits += 1
    else:
        raw_data = data.T

    # and normalize audio file in the [ -1 ; 1 ] range
    normalized_data = raw_data / 2 ** normalize_bits

    byte_per_frame = fs / opts.target_fps

    frame_start = 0
    frame_index = 0
    while frame_start < len(normalized_data):
        spectrum = abs(np.fft.rfft(normalized_data[frame_start:frame_start + 4096]))

        write_spectrum(spectrum[1:], frame_index, fs, opts)

        frame_start += byte_per_frame
        frame_index += 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
