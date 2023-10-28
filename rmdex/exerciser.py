""" Utilities for making and checking exercises
"""

import re
from functools import partial
import codecs

from statemachine import StateMachine, State

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


class ExerciseMachine(StateMachine):
    "A state machine to generate the exercise"

    default = State(initial=True)
    both_line = State()
    both_section = State()
    both_to_end = State()

    process_line = (
        default.to(both_line, cond='both_line_mark')
        | default.to(both_to_end, cond='both_end_mark')
        | default.to(both_section, cond='both_section_mark')
        | default.to.itself(on='default_line')
        | both_line.to(default, on='append_line')
        | both_section.to(default, cond='both_section_mark')
        | both_section.to.itself(on='append_line')
        | both_to_end.to.itself(on='append_line')
    )

    def __init__(self, code):
        self.code = code
        super().__init__()

    def both_line_mark(self, line):
        return line.strip() == '#<--'

    def both_section_mark(self, line):
        return line.lstrip() == '#<-'

    def both_end_mark(self, line):
        return line.strip() == '#<->'

    def append_line(self, line):
        return line

    def default_line(self, line):
        sline = line.lstrip()
        # We allow "#<- " (with space(s)) as placeholder for blank line.
        if sline.startswith('#<- '):
           return line.replace('#<- ', '')
        if sline.startswith('#<-'):
            raise MarkupError('There must be a space after the #<- marker '
                              'unless it is a both-line marker or a '
                              'line on its own:\n' + self.code)
        if sline.startswith('#-'):
            return line
        return None

    def parse(self):
        lines = [self.process_line(line) for line in self.code.splitlines()]
        if self.current_state == self.both_line:
            raise MarkupError('No line after #<-- marker:\n' + self.code)
        if self.current_state == self.both_section:
            raise MarkupError('Missing a closing #<- marker:\n' + self.code)
        return '\n'.join(L for L in lines if L is not None) + '\n'


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
    return ExerciseMachine(code).parse()


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
    """ Process question chunks in notebook `mb`, with function `func`

    Parameters
    ----------
    mb : :class:`RNotebook`
    func : callable

    Returns
    -------
    nb_str : str
        Notebook in RMarkdown string form.
    """
    chunks = question_chunks(nb)
    chunks = [Chunk(func(c.code),
                    c.language,
                    c.start_line,
                    c.end_line)
              for c in chunks]
    return replace_chunks(nb.nb_str, chunks)


MODEL_ANSWER_RE = re.compile(r"""
(?P<header>
^\s*<!--\s*\#region\s*{["']manual_grade["']\s*:\s*true,.*?}\s*-->)
\s*$
(?P<model_answer>.*?)
(?P<footer>
^\s*<!--\s*\#endregion\s*-->)$""", flags=re.M | re.S | re.VERBOSE)


def strip_model_answers(
    nb_str,
    replacement='*Write your answer here, replacing this text.*'):
    """ Strip model answers from manual grading questions

    Parameters
    ----------
    nb_str : str
        Text of notebook
    replacement : str, optional

    Returns
    -------
    mod_str : str
        Maybe modified text of notebook

    Notes
    -----
    Looks for model answers of form::

        <!-- #region {"manual_grade": true, "manual_problem_id": "my_q"} -->
        This is a model answer that the students should not see
        <!-- #endregion -->

    and replaces to give::

        <!-- #region {"manual_grade": true, "manual_problem_id": "my_q"} -->
        *Write your answer here, replacing this text.*
        <!-- #endregion -->
    """
    return MODEL_ANSWER_RE.sub(
                    rf'\g<header>\n{replacement}\n\g<footer>',
                    nb_str)


def make_filtered(template_str, q_filt_func=None, str_filt_func=None):
    """ Filter `template_str` with question and string filter functions

    Parameters
    ----------
    template_str : str
        String containing RMarkdown notebook
    q_filt_func : None or callable, optional
        Callable to filter questions, apassed to :func:`process_questions`
    str_filt_func : None or callable, optional
        Callable to filter text.

    Returns
    -------
    out_nb_str : str
        Filtered notebook text.
    """
    out_nb = loads(template_str)
    q_filt_func = (lambda x : x) if q_filt_func is None else q_filt_func
    out_nb_str = process_questions(out_nb, q_filt_func)
    if str_filt_func:
        out_nb_str = str_filt_func(out_nb_str)
    return out_nb_str


make_exercise = partial(make_filtered, q_filt_func=template2exercise,
                        str_filt_func=strip_model_answers)

make_solution = partial(make_filtered, q_filt_func=template2solution)


def check_marks(nb_str, total=100):
    check_chunk_marks(question_chunks(loads(nb_str)), total)


def make_check_exercise(solution_str, total=100):
    exercise = make_exercise(solution_str)
    check_marks(exercise, total)
    return exercise
