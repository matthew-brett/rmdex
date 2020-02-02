""" Utilities for making and checking exercises
"""

import re
from functools import partial
import codecs

from rnbgrader import loads
from rnbgrader.nbparser import Chunk


class ExerciseError(RuntimeError): pass

class MarkError(ExerciseError): pass

class MarkupError(ExerciseError): pass


MARK_RE = re.compile(r"""^\s*\#-
                     \s+([0-9.]+)
                     \s+marks
                     \s+/
                     \s+([0-9.]+)
                     \s+\(total
                     \s+([0-9.]+)""", re.VERBOSE)


EX_COMMENT_RE = re.compile(r'^\s*#<?-', re.M)


def read_utf8(fname):
    with codecs.open(fname, 'r', encoding='utf8') as fobj:
        return fobj.read()


def write_utf8(fname, contents):
    with codecs.open(fname, 'w', encoding='utf8') as fobj:
        return fobj.write(contents)


def question_chunks(nb):
    return [chunk for chunk in nb.chunks if EX_COMMENT_RE.search(chunk.code)]


def get_marks(code):
    for line in code.splitlines():
        match = MARK_RE.match(line)
        if match is not None:
            return tuple(float(v) for v in match.groups())
    return None, None, None


def check_chunk_marks(question_chunks, total=100):
    running = 0
    exp_running = 0
    for chunk in question_chunks:
        msg = (f'chunk:\n\n{chunk.code}\n' +
               f'Chunk starts at line {chunk.start_line}')
        mark, out_of, exp_running = get_marks(chunk.code)
        if mark is None:
            raise MarkError(f'No mark in {msg}')
        if out_of != total:
            raise MarkError(f'Total {out_of} should be {total} in {msg}')
        running += mark
        if running != exp_running:
            raise MarkError(
                f'Running total {running} incorrect; ' +
                f'should be {exp_running} in {msg}')
    if exp_running != total:
        raise MarkError(f'Grand total {exp_running} but should be {total}')


def add_marks(code, total, always=False):
    if not always and get_marks(code)[0] is not None:
        return code
    lines = []
    in_comments = True
    for line in code.splitlines(keepends=True):
        if in_comments and not EX_COMMENT_RE.match(line):
            lines.append('#-  marks / {} (total  so far)\n'.format(total))
            in_comments = False
        lines.append(line)
    return ''.join(lines)


def template2exercise(code):
    """ Convert `code` marked up for exercise + solution to exercise format.

    Parameters
    ----------
    code : str
        String containing one or more lines of code.

    Returns
    -------
    exercise_code : str
        Code as it will appear in the exercise version.
    """
    lines = []
    state = 'default'
    for line in code.splitlines():
        if state == 'both-line':
            lines.append(line)
            state = 'default'
            continue
        sline = line.lstrip()
        is_both_mark = sline == '#<-'  # Start/end of both-mark
        if state == 'both-section':
            if is_both_mark:
                state = 'default'
                continue
        if state in ('both-section', 'both-to-end'):
            lines.append(line)
            continue
        # Must be default state
        assert state == 'default'
        if is_both_mark:
            state = 'both-section'
            continue
        if sline == '#<->':  # both-to-end marker
            state = 'both-to-end'
            continue
        elif sline == '#<--':  # both-line marker - next line ex + solution.
            state = 'both-line'
            continue
        if not sline.startswith('#'):
            continue
        if sline.startswith('#<- '):
            lines.append(line.replace('#<- ', ''))
        elif sline.startswith('#<-'):
            raise MarkupError('There must be a space after the #<- marker '
                              'unless it is a both-line marker or a '
                              'line on its own:\n' + code)
        elif sline.startswith('#-'):
            lines.append(line)
    if state == 'both-line':
        raise MarkupError('No line after #<-- marker:\n' + code)
    if state == 'both-section':
        raise MarkupError('Missing a closing #<- marker:\n' + code)
    return '\n'.join(lines) + '\n'


def template2solution(code):
    """ Convert `code` marked up for exercise + solution to solution format.

    Parameters
    ----------
    code : str
        String containing one or more lines of code.

    Returns
    -------
    solution_code : str
        Code as it will appear in the solution version.
    """
    lines = [L for L in code.splitlines() if not L.strip().startswith('#<-')]
    return '\n'.join(lines) + '\n'


def replace_chunks(nb_str, chunks):
    lines = nb_str.splitlines(keepends=True)
    for chunk in chunks:
        lines[chunk.start_line] = chunk.code
        for line_no in range(chunk.start_line + 1, chunk.end_line + 1):
            lines[line_no] = ''
    return ''.join(lines)


def process_questions(nb, func):
    chunks = question_chunks(nb)
    chunks = [Chunk(func(c.code),
                    c.language,
                    c.start_line,
                    c.end_line)
              for c in chunks]
    return replace_chunks(nb.nb_str, chunks)


def make_filtered(template_str, filt_func):
    return process_questions(loads(template_str), filt_func)


make_exercise = partial(make_filtered, filt_func=template2exercise)

make_solution = partial(make_filtered, filt_func=template2solution)


def check_marks(nb_str, total=100):
    check_chunk_marks(question_chunks(loads(nb_str)), total)


def make_check_exercise(solution_str, total=100):
    exercise = make_exercise(solution_str)
    check_marks(exercise, total)
    return exercise
