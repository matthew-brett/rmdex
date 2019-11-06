""" Tests for exerciser module
"""

from os.path import dirname, join as pjoin

from rnbgrader import load, loads
from rnbgrader.nbparser import RNotebook

from rmdex.exerciser import (make_check_exercise, make_exercise, make_solution,
                             get_marks, check_marks, check_chunk_marks,
                             question_chunks, MARK_RE, template2exercise,
                             MarkupError, read_utf8)

import pytest


HERE = dirname(__file__)
SOLUTION_FNAME = pjoin(HERE, 'solution.Rmd')
EXERCISE_FNAME = pjoin(HERE, 'exercise.Rmd')
SOLUTION_STR = read_utf8(SOLUTION_FNAME)
EXERCISE_STR = read_utf8(EXERCISE_FNAME)

TEMPLATE_FNAME = pjoin(HERE, 'template.Rmd')
T_EXERCISE_FNAME = pjoin(HERE, 'template_exercise.Rmd')
T_SOLUTION_FNAME = pjoin(HERE, 'template_solution.Rmd')
TEMPLATE_STR = read_utf8(TEMPLATE_FNAME)
T_EXERCISE_STR = read_utf8(T_EXERCISE_FNAME)
T_SOLUTION_STR = read_utf8(T_SOLUTION_FNAME)


def test_make_check_exercise():
    assert make_check_exercise(SOLUTION_STR) == EXERCISE_STR


def test_make_exercise():
    nb = load(SOLUTION_FNAME)
    check_marks(nb.nb_str)
    exercise = make_exercise(SOLUTION_STR)
    assert exercise == EXERCISE_STR
    check_marks(exercise)
    check_chunk_marks(question_chunks(loads(exercise)))
    nb = load(TEMPLATE_FNAME)
    exercise = make_exercise(TEMPLATE_STR)
    assert exercise == T_EXERCISE_STR


def test_make_solution():
    # No changes for the basic example (no #<- lines)
    solution = make_solution(SOLUTION_STR)
    assert solution == SOLUTION_STR
    # The Python example does have #<- lines.
    solution = make_solution(TEMPLATE_STR)
    assert solution == T_SOLUTION_STR


def test_question_chunks():
    nb = load(SOLUTION_FNAME)
    chunks = question_chunks(nb)
    assert len(chunks) == 15
    nb = loads("""\
Some text

```{python}
# Not question
a = 1
```

More text.

```{r}
# Still not question
b <- 2
```

Another line of text.

```{r}
#- This is a question.
c <- 3
```

Text.

Continues.

```{python}
# This is a question too.
#<- print("hello")
```

Typing is easy but boring.

```{r}
# This is not question, again.
d <- 4
```

```{python}
#- This is a question, again.
e <- 4
```
""")
    chunks = question_chunks(nb)
    assert len(chunks) == 3
    assert [c.code for c in chunks] == [
        '#- This is a question.\nc <- 3\n',
        '# This is a question too.\n#<- print("hello")\n',
        '#- This is a question, again.\ne <- 4\n']
    assert [c.language for c in chunks] == ['r', 'python', 'python']


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


def test_template2exercise():
    t2e = template2exercise
    assert t2e('#- foo\n#- bar') == '#- foo\n#- bar\n'
    assert t2e('#- foo\na = 1\n#- bar') == '#- foo\n#- bar\n'
    assert t2e('#- foo\na = 1\n# bar') == '#- foo\n'
    assert t2e('#- foo\n#<- a = ?\n# bar') == '#- foo\na = ?\n'
    assert t2e('#- foo\n#<- a = ?\n#- bar') == '#- foo\na = ?\n#- bar\n'
    assert (t2e('#- foo\n  #<- a = ?\n#- bar') ==
            '#- foo\n  a = ?\n#- bar\n')
    with pytest.raises(MarkupError):  # No space after #<-
        t2e('#- foo\n#<-a = ?\n# bar\n')
    # With space suffix, marker adds a blank line to the solution.
    assert t2e('#- foo\n#<- \n# bar') == '#- foo\n\n'
    with pytest.raises(MarkupError):  # No closing #<-
        t2e('#- foo\n#<-\n# bar\n')
    # With a closing marker - include solution code in exercise.
    assert (t2e('#- foo\n#<-\n# bar\na = 1\n#<-\n') ==
            '#- foo\n# bar\na = 1\n')
    # Check stuff after both chunk still gets stripped.
    assert (t2e(
        '#- foo\n#<-\n# bar\na = 1\n#<-\nb = 2\n') ==
        '#- foo\n# bar\na = 1\n')
    # And that one-line #<- still works.
    assert (t2e(
        '#- foo\n#<-\n# bar\na = 1\n#<-\n#<- b = 2\n') ==
        '#- foo\n# bar\na = 1\nb = 2\n')
    # Test a second chunk.
    assert (t2e(
        '#- foo\n#<-\n# bar\na = 1\n#<-\nb = 2\n'
        '#<-\nc = 2\nd=3\n#<-\ne = 4\n') ==
        ('#- foo\n# bar\na = 1\n'
         'c = 2\nd=3\n'))
