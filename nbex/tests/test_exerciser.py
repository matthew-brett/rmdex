""" Tests for exerciser module
"""

from os.path import dirname, join as pjoin
import codecs

from rnbgrader import load, loads

from nbex.exerciser import (make_check_exercise, make_exercise, get_marks,
                            solution2exercise, check_exercise,
                            check_chunk_marks, question_chunks, MARK_RE,
                            strip_code
                           )


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
    exercise = solution2exercise(nb)
    check_exercise(exercise)
    check_chunk_marks(question_chunks(loads(exercise)))


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
    assert strip_code('#- foo\n#- bar') == '#- foo\n#- bar'
    assert strip_code('#- foo\na = 1\n#- bar') == '#- foo\n#- bar'
    assert strip_code('#- foo\na = 1\n# bar') == '#- foo\n'
    assert strip_code('#- foo\n#<- a = ?\n# bar') == '#- foo\na = ?\n'
    assert strip_code('#- foo\n#<- a = ?\n#- bar') == '#- foo\na = ?\n#- bar'
    assert (strip_code('#- foo\n  #<- a = ?\n#- bar') ==
            '#- foo\n  a = ?\n#- bar')


