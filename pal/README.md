# Usage

 1. Run `python palencode.py BBC2_testcard_F_2.jpg` (or your own image - must be 768x576px for.. reasons). This will generate `output.bin`.
 2. Open pal.grc, fix the path to `output.bin`, adjust TX frequency and gain.
 3. Run.

# Known issues

 * Currently it's not really PAL as it's black and white only
 * It's specific to PAL standard I, and so far only tested on UK TVs
