""" Utilities for making and checking exercises
"""

import re

from rnbgrader import loads
from rnbgrader.nbparser import Chunk


MARK_RE = re.compile(r"""^\s*\#-
                     \s+(\d+)
                     \s+marks
                     \s+/
                     \s+(\d+)
                     \s+\(total
                     \s+(\d+)""", re.VERBOSE)



def question_chunks(nb):
    return [chunk for chunk in nb.chunks
            if re.search('^\s*#-', chunk.code, re.M)]


def get_marks(code):
    for line in code.splitlines():
        match = MARK_RE.match(line)
        if match is not None:
            return tuple(float(v) for v in match.groups())
    return None, None, None


def check_chunk_marks(question_chunks, total=100):
    running = 0
    for chunk in question_chunks:
        msg = ' in chunk:\n\n{}\n\nat line {}'.format(
            chunk.code, chunk.start_line)
        mark, out_of, exp_running = get_marks(chunk.code)
        assert mark is not None, 'No mark' + msg
        assert out_of == total, 'Total incorrect' + msg
        running += mark
        assert running == exp_running, 'Running total incorrect' + msg
    assert exp_running == total, 'Grand total {} not the expected {}'.format(
        exp_running, total)


def strip_code(code):
    lines = []
    for line in code.splitlines(keepends=True):
        sline = line.strip()
        if not sline.startswith('#'):
            continue
        if sline.startswith('#<- '):
            lines.append(line.replace('#<- ', ''))
        elif sline.startswith('#-'):
            lines.append(line)
    return ''.join(lines)


def replace_chunks(nb_str, chunks):
    lines = nb_str.splitlines(keepends=True)
    for chunk in chunks:
        lines[chunk.start_line] = chunk.code
        for line_no in range(chunk.start_line + 1, chunk.end_line + 1):
            lines[line_no] = ''
    return ''.join(lines)


def solution2exercise(nb):
    chunks = question_chunks(nb)
    chunks = [Chunk(strip_code(c.code),
                    c.language,
                    c.start_line,
                    c.end_line)
              for c in chunks]
    return replace_chunks(nb.nb_str, chunks)


def make_exercise(solution_str):
    nb = loads(solution_str)
    return solution2exercise(nb)


def check_exercise(exercise):
    check_chunk_marks(question_chunks(loads(exercise)))


def make_check_exercise(solution_str):
    exercise = make_exercise(solution_str)
    check_exercise(exercise)
    return exercise
