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

from argparse import ArgumentParser, RawDescriptionHelpFormatter

from rmdex.exerciser import (make_exercise, make_solution, check_marks,
                             read_utf8, write_utf8)


CONVERTERS = {
    'exercise': make_exercise,
    'solution': make_solution,
}


def get_parser():
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("template_rmd", help="filename of template notebook")
    parser.add_argument("exercise_rmd", nargs='?', default='_',
                        help="output filename for exercise notebook; "
                        "default is '_' meaning, omit write of exercise")
    parser.add_argument("solution_rmd", nargs='?', default='_',
                        help="output filename for solution notebook; "
                        "default is '_' meaning, omit write of solution")
    parser.add_argument("--check-marks", action="store_true",
                        help="Enable checking of mark totals")
    parser.add_argument("--total", type=int, default=100,
                        help="Total marks that mark check should sum to")
    return parser


def main_func():
    args = get_parser().parse_args()
    nb_fname = args.template_rmd
    ex_fname = None if args.exercise_rmd == '_' else args.exercise_rmd
    soln_fname = None if args.solution_rmd == '_' else args.solution_rmd
    nb_str = read_utf8(nb_fname)
    # Always create exercise in memory, to check marks.
    if args.check_marks or ex_fname is not None:
        ex_nb = make_exercise(nb_str)
        if args.check_marks:
            check_marks(ex_nb, args.total)
        if ex_fname is not None:
            write_utf8(ex_fname, ex_nb)
    if soln_fname is not None:
        soln_nb = make_solution(nb_str)
        write_utf8(soln_fname, soln_nb)
