""" Command line interface to RmdEx

* Get code chunks
* Filter code chunks for presence of #- comments, indicating this is a
  question.  Code chunks #<- comments are also questions.
* Comments starting #<- (followed by space) should go into exercise without #<-
* When the whole line is exactly #<- this is a "Both Marker".  It indicates
  that all lines up to the next Both Marker should go in both exercise and
  solution.
* Check that each question has marks recorded, if flag says so to do.
* Check that marks add up to given total.
* Generate exercise, where code has been removed.
"""

import codecs
from argparse import ArgumentParser

from rmdex import make_exercise, check_marks
from rnbgrader.nbparser import read_file


def get_parser():
    parser = ArgumentParser(description='Check solution, generate exercise')
    parser.add_argument("solution_rmd", help="filename of solution notebook")
    parser.add_argument("exercise_rmd",
                        help="filename for output exercise notebook")
    parser.add_argument("--total", type=int, default=100, help="Total marks")
    parser.add_argument("--no-check-marks", action="store_true",
                        help="Disable checking of mark totals")
    return parser


def main_func():
    args = get_parser().parse_args()
    nb_fname = args.solution_rmd
    out_fname = args.exercise_rmd
    exercise = make_exercise(read_file(nb_fname))
    if not args.no_check_marks:
        check_marks(exercise, args.total)
    with codecs.open(out_fname, 'w', encoding='utf8') as fobj:
        fobj.write(exercise)
