###################################################################
rmdex - utilities for generating and checking Rmd notebook exercises
###################################################################

.. shared-text-body

**********
Quickstart
**********

The main things this library can do are:

* generate an exercise notebook from a solution notebook, given some markup in
  the comments of the solution notebook, and
* check mark totals specified in the comments, to make sure they add up
  correctly.

The utility expects the comments in *code cells* to have some extra markup to
tell it what to do.

The comment notation is as follows:

* An *exercise comment* is any comment beginning ``#-``.  These pass
  unmodified to the exercise notebook.
* An *exercise insertion comment* is any comment beginning ``#<-`` (in fact,
  there must be a space following).  This signals that all text following the
  ``#<-`` should go directly into the exercise cell.  It allows the solution
  to specify template code.
* Any other code lines, including ordinary comments beginning ``#`` get
  stripped from the solution, to form the exercise.
* A *marks comment* is a *exercise comment* of form ``#- 5 marks / 100 (total
  10 marks`` where 5 is the marks for this cell, 100 is the total for the
  whole exercise, and 10 is the total marks if all correct up to this point
  (including this cell).

For example, the solution may have a cell like this::

    ```{r}
    #- Here you will do a simple assignment.
    #- More description of the assignment.
    #- 5 marks / 100 (total 10 marks so far).
    # This comment gets stripped from the exercise version of the cell.
    # Also this one.  The next line adds the text after #<- to the exercise.
    #<- my_variable = ...
    # This comment and the next code line do not appear in the exercise.
    my_variable <- 10
    ```

The solution cell above results in the following in the exercise version::

    ```{r}
    #- Here you will do a simple assignment.
    #- More description of the assignment.
    #- 5 marks / 100 (total 10 marks so far).
    my_variable <- ...
    ```

The script ``rmdex_check`` reads the solution, checks the mark totals, and
generates the exercise.

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
automatically under Python versions 3.4 through 3.6.

The latest released version is at https://pypi.python.org/pypi/rmdex

*****
Tests
*****

* Install ``rmdex``;
* Install the pytest_ testing framework::

    pip install pytest

* Run the tests with::

    py.test rmdex

*******
Support
*******

Please put up issues on the `rmdex issue tracker`_.

.. standalone-references

.. |rmdex-documentation| replace:: `rmdex documentation`_
.. _rmdex documentation:
    https://matthew-brett.github.com/rmdex/index.html
.. _documentation: https://matthew-brett.github.com/rmdex
.. _pandoc: http://pandoc.org
.. _jupyter: jupyter.org
.. _homebrew: brew.sh
.. _sphinx: http://sphinx-doc.org
.. _rest: http://docutils.sourceforge.net/rst.html
.. _rmdex issue tracker: https://github.com/matthew-brett/rmdex/issues
.. _pytest: https://pytest.org
.. _mock: https://github.com/testing-cabal/mock
