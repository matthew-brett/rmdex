"""Command line interface to RmdEx

* Get code chunks
* Filter code chunks for presence of #- comments, indicating this is a
  question.  Code chunks #<- comments are also questions.
* Comments starting #<- (followed by space) should go into exercise with
  #<- prefix stripped.  Such comments removed in the solution.
* When the whole line is exactly #<- this is a "Both Marker".  It indicates
  that all lines up to the next Both Marker should go in both exercise and
  solution.  Both Markers always removed from exercise and solution.
* Check that each question has marks recorded, when check-marks option
  specified.
* Check that marks add up to given total, when check-marks option
  specified.
* Generate exercise or solution, with modified question chunks.
"""

import codecs
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from rmdex import make_exercise, make_solution, check_marks
from rnbgrader.nbparser import read_file


CONVERTERS = {
    'exercise': make_exercise,
    'solution': make_solution,
}


def get_parser():
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("template_rmd", help="filename of template notebook")
    parser.add_argument("output_rmd", help="filename for output notebook")
    parser.add_argument("--to", default='exercise',
                        help="Can be 'exercise' or 'solution'. Default is "
                        "'exercise'")
    parser.add_argument("--total", type=int, default=100, help="Total marks")
    parser.add_argument("--check-marks", action="store_true",
                        help="Enable checking of mark totals")
    return parser


def main_func():
    args = get_parser().parse_args()
    nb_fname = args.template_rmd
    out_fname = args.output_rmd
    if args.to not in CONVERTERS:
        raise RuntimeError("Converter must be 'exercise' or 'solution' "
                           f"but is '{args.to}'")
    out_nb = CONVERTERS[args.to](read_file(nb_fname))
    if args.check_marks:
        check_marks(out_nb, args.total)
    with codecs.open(out_fname, 'w', encoding='utf8') as fobj:
        fobj.write(out_nb)
