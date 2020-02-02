####################################################################
Rmdex - utilities for generating and checking Rmd notebook exercises
####################################################################

.. shared-text-body

**********
Quickstart
**********

The main things this library can do are:

* generate an exercise notebook and a solution notebook from a template
  notebook, given some markup in the comments of the template notebook, and
* check mark totals specified in the comments, to make sure they add up
  correctly.

The utility expects the comments in *code cells* to have some extra markup to
tell it what to do.

It is equally happy processing `R notebooks`_ in RMarkdown_ format, or
Jupyter_ notebooks saved as RMarkdown, probably using Jupytext_.  You can see
examples of use on Jupyter notebooks in
https://github.com/matthew-brett/cfd2019/tree/master/_ok_exercises.

The comment notation is as follows:

* An exercise cell (Jupyter) or chunk (R notebook) is any cell / chunk with an
  comment starting ``#-`` (an exercise comment) or starting ``#<-`` (see
  below). Rmdex will only modify exercise cells / chunks in the output exercise
  and solution.
* An *exercise comment* is any comment beginning ``#-``.  These pass
  unmodified to the exercise and solution notebooks.
* An *exercise insertion comment* is any comment beginning ``#<-`` *followed
  by a space*. The text following will be a line that should not go in the
  solution, but should go in the exercise.  It allows the template to suggest
  code to the user, that will not appear in the solution. The code after this
  mark need not be valid syntax.
* A *both-section marker* is a line consisting of ``#<-`` *followed
  immediately by a new line character*. This indicates that all subsequent
  lines, up to the next ``#<-`` line (both-section marker), should go into the
  exercise and the solution.
* A *both-line marker* is a line consisting of ``#<--`` *followed immediately
  by a new line character*.  The next line goes into the solution and the
  exercise.
* If there is any line starting ``#<-`` and followed by anything other than
  space, a new line, or a ``-``, this is an error.
* Any other code lines, including ordinary comments beginning ``#``, get
  stripped from the exercise.  They do appear in the solution.
* A *marks comment* is a *exercise comment* of form ``#- 5 marks / 100 (total
  10 marks so far)`` where 5 is the marks for this cell, 100 is the total for
  the whole exercise, and 10 is the total marks if all answers are correct up
  to this point (including this cell).  You can use the ``--check-marks``
  option to the main ``rmdex`` utility to check the consistency of these
  numbers (see below).

For example, the template may have a cell like this::

    ```{r}
    #- Here you will do a simple assignment.
    #- More description of the assignment.
    #- 5 marks / 100 (total 10 marks so far).
    # This comment gets stripped from the exercise version of the cell.
    # Also this one.  The next line adds the text after #<- to the exercise.
    #<- my_variable = ...
    # This comment and the next code line do not appear in the exercise.
    my_variable = 10
    #<-
    # This comment does appear in the exercise, as well as the following code.
    another_variable = 11
    print("Something")
    #<-
    #<--
    # This line follows the both-line marker, and appears in the exercise.
    # This line does not.
    # Starting at the previous line, we resume normal service.  This and
    # the next line of comments do not appear in the exercise.
    #
    # The following marker causes everything to the end of the cell/chunk
    # to appear in both exercise and solution:
    #<->
    print('This line appears in the exercise and solution')
    print('as does this line')
    ```

The template cell above results in the following in the exercise version::

    ```{r}
    #- Here you will do a simple assignment.
    #- More description of the assignment.
    #- 5 marks / 100 (total 10 marks so far).
    my_variable = ...
    # This comment does appear in the exercise, as well as the following code.
    another_variable = 11
    print("Something")
    # This line follows the both-line marker, and appears in the exercise.
    print('This line appears in the exercise and solution')
    print('as does this line')
    ```

The solution will have::

    ```{r}
    #- Here you will do a simple assignment.
    #- More description of the assignment.
    #- 5 marks / 100 (total 10 marks so far).
    # This comment gets stripped from the exercise version of the cell.
    # Also this one.  The next line adds the text after #<- to the exercise.
    # This comment and the next code line do not appear in the exercise.
    my_variable = 10
    # This comment does appear in the exercise, as well as the following code.
    another_variable = 11
    print("Something")
    # This line follows the both-line marker, and appears in the exercise.
    # This line does not.
    # Starting at the previous line, we resume normal service.  This and
    # the next line of comments do not appear in the exercise.
    #
    # The following marker causes everything to the end of the cell/chunk
    # to appear in both exercise and solution:
    print('This line appears in the exercise and solution')
    print('as does this line')
    ```

The script ``rmdex`` reads the templates, checks the mark totals (with the
option ``--check-marks``), and generates the exercise.  It can also generate the solution.  Here are some examples of use:

.. code-block:: console

    # Generate the exercise from the template.
    rmdex template_notebook.Rmd exercise_notebook.Rmd

    # Generate the exercise and solution from the template.
    rmdex template_notebook.Rmd exercise_notebook.Rmd solution_notebook.Rmd

    # Check the marks total in the exercise, but do not write the exercise.
    rmdex --check-marks template_notebook.Rmd

    # Check the marks total in the exercise, and write the exercise.
    rmdex --check-marks template_notebook.Rmd exercise_notebook.Rmd

    # Write the solution only.
    rmdex template_notebook.Rmd _ solution_notebook.Rmd

************
Installation
************

::

    pip install rmdex

****
Code
****

See https://github.com/matthew-brett/rmdex

Released under the BSD two-clause license - see the file ``LICENSE`` in the
source distribution.

`travis-ci <https://travis-ci.org/matthew-brett/rmdex>`_ kindly tests the code
automatically under Python versions 3.6 through 3.8.

The latest released version is at https://pypi.python.org/pypi/rmdex

*****
Tests
*****

* Install ``rmdex``;
* Install the pytest_ testing framework::

    pip install pytest

* Run the tests with::

    pytest rmdex

*******
Support
*******

Please put up issues on the `rmdex issue tracker`_.

.. standalone-references

.. |rmdex-documentation| replace:: `rmdex documentation`_
.. _rmdex documentation:
    https://matthew-brett.github.com/rmdex/index.html
.. _documentation: https://matthew-brett.github.com/rmdex
.. _pandoc: https://pandoc.org
.. _jupyter: https://jupyter.org
.. _RMarkdown: https://rmarkdown.rstudio.com
.. _R notebooks: https://bookdown.org/yihui/rmarkdown/notebook.html
.. _Jupytext: https://github.com/mwouts/jupytext
.. _homebrew: https://brew.sh
.. _sphinx: https://www.sphinx-doc.org
.. _rest: http://docutils.sourceforge.net/rst.html
.. _rmdex issue tracker: https://github.com/matthew-brett/rmdex/issues
.. _pytest: https://pytest.org
