# wavprogress, Generate wav file progression as images
# Copyright (C) 2016  Olivier Jolly
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging
import sys

import numpy as np
import os
from PIL import Image, ImageDraw
from wavfile import read as wav_read

__all__ = []
__version__ = 0.1
__date__ = '2016-05-22'
__updated__ = '2016-05-22'
__author__ = 'olivier@pcedev.com'


def get_rms(data):
    return np.sqrt(np.mean(np.square(data)))


def main(argv=None):
    program_name = os.path.basename(sys.argv[0])
    program_version = "v" + str(__version__)
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_longdesc = '''Generate wav files progression as images'''
    program_license = "GPL v3+ 2016 Olivier Jolly"

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
        parser.add_argument("-r", "--framerate", dest="target_fps", default=30,
                            help="output framerate [default: %(default)s]")
        # parser.add_argument("-R", "--renderer", dest="renderer", default=0, type=int, choices=range(len(RENDERERS)),
        #                     help="which renderer to use to display bars (0=filled, 1=hollow, "
        #                          "2=symetrical filled, 3=symetrical hollow)")
        parser.add_argument("-v", "--version", action="version", version=program_version_string)

        parser.add_argument("-w", "--width", dest="width", default=512, type=int,
                            help="width in output images [in px, default: %(default)s]")
        parser.add_argument("--height", dest="height", default=32, type=int,
                            help="height in output images [in px, default: %(default)s]")

        parser.add_argument("-C", "--color", dest="color", default='FFFFFFFF', type=str,
                            help="hexa color of bars [RRGGBB or RRGGBBAA, default: %(default)s]")

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

    # convert hexa in input to RGBA tuple
    opts.color = (
        int(opts.color[0:2], 16),
        int(opts.color[2:4], 16),
        int(opts.color[4:6], 16),
        int(opts.color[6:8], 16) if len(opts.color) > 6 else 255
    )

    # load input file
    fs, data = wav_read(opts.input_filename)

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

    # work with normalized_data

    time_hop = float(fs) / opts.target_fps
    frame_per_slice = (len(raw_data) / time_hop) / opts.width

    rms = [get_rms(normalized_data[frame_idx * time_hop:(frame_idx + 1) * time_hop]) for frame_idx in
           range(int(len(raw_data) / time_hop))]

    # normalize rms over the song length
    rms /= np.max(rms)

    heights = np.zeros(opts.width)

    for frame in range(len(rms)):

        print("{0:6}/{1:6}".format(frame, len(rms)), end="\r")

        current_slice, remainder_in_slice = divmod(frame, frame_per_slice)
        current_slice = int(current_slice)
        remainder_in_slice = int(remainder_in_slice)

        # update only the previous slice, for large enough fps (ie not progressing more than 1px per frame), it's
        # enough
        if current_slice > 0:
            heights[current_slice - 1] = np.mean(
                rms[int((current_slice - 1) * frame_per_slice):int((current_slice) * frame_per_slice)])

        if remainder_in_slice > 0:
            heights[current_slice:current_slice + 1] = rms[frame]

        # np.mean(rms[int(current_slice * frame_per_slice): int(current_slice * frame_per_slice + remainder_in_slice)])

        image = Image.new("RGBA", (opts.width, opts.height))
        draw = ImageDraw.Draw(image)

        for x, y in enumerate(heights):
            color = opts.color

            if x < current_slice - 10:
                color = (color[0], color[1], color[2], color[3] // 2)
            elif x >= current_slice - 10 and x < current_slice:
                color = (
                    color[0], color[1], color[2],
                    int(color[3] * 0.5 * (1 + np.cos((current_slice - x) / 10 * np.pi / 2))))
            draw.line([x, opts.height * (1 - y) / 2, x, opts.height * (1 + y) / 2], fill=color)

        image.save(opts.output_filename_mask.format(frame))

        del draw

    return 0


if __name__ == "__main__":
    sys.exit(main())
