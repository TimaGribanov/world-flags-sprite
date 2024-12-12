#!/usr/bin/env python2

import sys
import imread
import tempfile
import subprocess
import os

def append_images(orig):
    def scale(out, sz):
        subprocess.check_call(["convert", orig,
                               "-scale", sz,
                               out])
        subprocess.check_call(["convert", out,
                               "-background", "none",
                               "-gravity", "center",
                               "-extent", sz,
                               out])
    def append(f1, f2):
        subprocess.check_call(["convert",
                               f1, f2,
                               "-append", f1])

    tmpdir = tempfile.mkdtemp()
    out_32 = os.path.join(tmpdir, "32.png")
    scale(out_32, "32x32")
    append("images/flags32.png", out_32)

    # sanity checks
    sh32 = imread.imread("images/flags32.png").shape
    assert sh32[0] % 32 == 0
    assert sh32[1] == 32
    return sh32[0] - 32

if __name__ == '__main__':
    try:
        name, code, image = sys.argv[1:]
    except ValueError:
        print "usage: {} name code image".format(sys.argv[0])
        sys.exit(1)

    # validate the code - 2 lower case letters or starts with _
    is_2_letter = (len(code) == 2 and code == code.lower() and code.isalpha())
    assert is_2_letter or (code[0] == '_')

    # append the new images
    offset_32 = append_images(image)

    # add to the CSS
    open("stylesheets/flags32.css", "a").write(".f32 .{}{{background-position:0 -{}px;}}\n".format(code, offset_32))

    # and the SCSS
    lines32 = open("stylesheets/flags32.scss").readlines()
    idx = [l.strip() for l in lines32].index('} // .f32 - DO NOT REMOVE THIS LINE')
    lines32.insert(idx, "    .{}{{background-position:0 -{}px;}}\n".format(code, offset_32))
    open("stylesheets/flags32.scss", "w").writelines(lines32)

    # and the index.html
    html_lines = open("index.html").readlines()
    indices = [i for i, l in enumerate(html_lines)
               if l.strip() == '<!-- DO NOT REMOVE THIS LINE - AUTOMATIC INSERTION MARK -->']
    assert len(indices) == 1
    # insert last entry first
    ABBR = code.upper() if is_2_letter else "  "
    html_lines.insert(indices[0], '<abbr>{}</abbr><li class="flag {}">{}</li><br/>\n'.format(ABBR, code, name))
    open("index.html", "w").writelines(html_lines)
