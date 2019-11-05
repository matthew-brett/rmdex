""" Tests for exerciser module
"""

from os.path import dirname, join as pjoin
import codecs

from rnbgrader import load, loads
from rnbgrader.nbparser import RNotebook

from rmdex.exerciser import (make_check_exercise, make_exercise, get_marks,
                            solution2exercise, check_marks,
                            check_chunk_marks, question_chunks, MARK_RE,
                            strip_code, MarkupError
                           )

import pytest

HERE = dirname(__file__)
SOLUTION_FNAME = pjoin(HERE, 'solution.Rmd')
EXERCISE_FNAME = pjoin(HERE, 'exercise.Rmd')
with codecs.open(SOLUTION_FNAME, 'r', encoding='utf8') as _fobj:
    SOLUTION_STR = _fobj.read()
with codecs.open(EXERCISE_FNAME, 'r', encoding='utf8') as _fobj:
    EXERCISE_STR = _fobj.read()


def test_make_check_exercise():
    assert make_exercise(SOLUTION_STR) == EXERCISE_STR
    assert make_check_exercise(SOLUTION_STR) == EXERCISE_STR


def test_solution2exercise():
    nb = load(SOLUTION_FNAME)
    check_marks(nb.nb_str)
    exercise = solution2exercise(nb)
    check_marks(exercise)
    check_chunk_marks(question_chunks(loads(exercise)))


def test_null_solution():
    # A notebook with no question cells doesn't result in an error.
    nb = RNotebook.from_string('')
    check_marks(nb.nb_str, 0)


def test_check_marks():
    nb = load(SOLUTION_FNAME)
    q_chunks = question_chunks(nb)
    check_chunk_marks(q_chunks)


def test_marks_re():
    assert MARK_RE.match(
        '#- 5 marks / 100 (total 95 so far).').groups() == ('5', '100', '95')


def test_marks():
    assert get_marks('#- 5 marks / 100 (total 95 so far).') == (5, 100, 95)


def test_strip_code():
    assert strip_code('#- foo\n#- bar') == '#- foo\n#- bar\n'
    assert strip_code('#- foo\na = 1\n#- bar') == '#- foo\n#- bar\n'
    assert strip_code('#- foo\na = 1\n# bar') == '#- foo\n'
    assert strip_code('#- foo\n#<- a = ?\n# bar') == '#- foo\na = ?\n'
    assert strip_code('#- foo\n#<- a = ?\n#- bar') == '#- foo\na = ?\n#- bar\n'
    assert (strip_code('#- foo\n  #<- a = ?\n#- bar') ==
            '#- foo\n  a = ?\n#- bar\n')
    with pytest.raises(MarkupError):  # No space after #<-
        strip_code('#- foo\n#<-a = ?\n# bar\n')
    # With space suffix, marker adds a blank line to the solution.
    assert strip_code('#- foo\n#<- \n# bar') == '#- foo\n\n'
    with pytest.raises(MarkupError):  # No closing #<-
        strip_code('#- foo\n#<-\n# bar\n')
    # With a closing marker - include solution code in exercise.
    assert (strip_code('#- foo\n#<-\n# bar\na = 1\n#<-\n') ==
            '#- foo\n# bar\na = 1\n')
    # Check stuff after both chunk still gets stripped.
    assert (strip_code(
        '#- foo\n#<-\n# bar\na = 1\n#<-\nb = 2\n') ==
        '#- foo\n# bar\na = 1\n')
    # And that one-line #<- still works.
    assert (strip_code(
        '#- foo\n#<-\n# bar\na = 1\n#<-\n#<- b = 2\n') ==
        '#- foo\n# bar\na = 1\nb = 2\n')
    # Test a second chunk.
    assert (strip_code(
        '#- foo\n#<-\n# bar\na = 1\n#<-\nb = 2\n'
        '#<-\nc = 2\nd=3\n#<-\ne = 4\n') ==
        ('#- foo\n# bar\na = 1\n'
         'c = 2\nd=3\n'))
