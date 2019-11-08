# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test scripts

Test running scripts
"""

import os
from os.path import abspath

from scripttester import ScriptTester

from rnbgrader.nbparser import read_file

from rnbgrader.tmpdirs import in_dtemp

from . import test_exerciser as te


runner = ScriptTester('rmdex', win_bin_ext='.exe')
run_command = runner.run_command


def script_test(func):
    # Decorator to label test as a script_test
    func.script_test = True
    return func


def assert_wd_fnames(fnames):
    assert sorted(os.listdir('.')) == list(fnames)


@script_test
def test_rmdex():
    script = 'rmdex'
    soln_fname = abspath(te.SOLUTION_FNAME)
    template_fname = abspath(te.TEMPLATE_FNAME)
    with in_dtemp():
        cmd = [script,
               soln_fname,
               'out.Rmd']
        code, stdout, stderr = run_command(cmd)
        assert_wd_fnames(['out.Rmd'])
        assert read_file('out.Rmd') == te.EXERCISE_STR
    with in_dtemp():
        # Output filename is optional.
        cmd = [script,
               soln_fname]
        code, stdout, stderr = run_command(cmd)
        assert_wd_fnames([])
    with in_dtemp():
        # Solution the same as template for first example.
        cmd = [script,
               soln_fname,
               'out1.Rmd',
               'out2.Rmd']
        code, stdout, stderr = run_command(cmd)
        assert_wd_fnames(['out1.Rmd', 'out2.Rmd'])
        assert read_file('out1.Rmd') == te.EXERCISE_STR
        assert read_file('out2.Rmd') == te.SOLUTION_STR
    with in_dtemp():
        # Exercise filename can be underscore - not written.
        cmd = [script,
               soln_fname,
               '_',
               'out3.Rmd']
        code, stdout, stderr = run_command(cmd)
        assert_wd_fnames(['out3.Rmd'])
        assert read_file('out3.Rmd') == te.SOLUTION_STR
    with in_dtemp():
        # Solution filename can be _ too (not that it's very useful).
        cmd = [script,
               soln_fname,
               'out4.Rmd',
               '_']
        code, stdout, stderr = run_command(cmd)
        assert_wd_fnames(['out4.Rmd'])
        assert read_file('out4.Rmd') == te.EXERCISE_STR
    with in_dtemp():
        # Check marks doesn't need an output filename.
        cmd = [script,
               '--check-marks',
               soln_fname]
        code, stdout, stderr = run_command(cmd)
        assert_wd_fnames([])
    with in_dtemp():
        # Second example, just output exercise.
        cmd = [script,
               template_fname,
               'out5.Rmd']
        code, stdout, stderr = run_command(cmd)
        assert_wd_fnames(['out5.Rmd'])
        assert read_file('out5.Rmd') == te.T_EXERCISE_STR
    with in_dtemp():
        # Second example, just output solution.
        cmd = [script,
               template_fname,
               '_',
               'out6.Rmd']
        code, stdout, stderr = run_command(cmd)
        assert read_file('out6.Rmd') == te.T_SOLUTION_STR
    with in_dtemp():
        # Second example, output both.
        cmd = [script,
               template_fname,
               'out7.Rmd',
               'out8.Rmd']
        code, stdout, stderr = run_command(cmd)
        assert_wd_fnames(['out7.Rmd', 'out8.Rmd'])
        assert read_file('out7.Rmd') == te.T_EXERCISE_STR
        assert read_file('out8.Rmd') == te.T_SOLUTION_STR
