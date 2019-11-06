# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test scripts

Test running scripts
"""

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



@script_test
def test_rmdex_check():
    script = 'rmdex'
    soln_fname = abspath(te.SOLUTION_FNAME)
    template_fname = abspath(te.TEMPLATE_FNAME)
    with in_dtemp():
        cmd = [script, soln_fname, 'out.Rmd']
        code, stdout, stderr = run_command(cmd)
        assert read_file('out.Rmd') == te.EXERCISE_STR
        cmd = [script,
               '--to=exercise',
               soln_fname,
               'out2.Rmd']
        code, stdout, stderr = run_command(cmd)
        assert read_file('out2.Rmd') == te.EXERCISE_STR
        cmd = [script,
               '--check-marks',
               soln_fname,
               'out3.Rmd']
        code, stdout, stderr = run_command(cmd)
        assert read_file('out3.Rmd') == te.EXERCISE_STR
        cmd = [script,
               template_fname,
               'out4.Rmd']
        code, stdout, stderr = run_command(cmd)
        assert read_file('out4.Rmd') == te.T_EXERCISE_STR
        cmd = [script,
               '--to', 'solution',
               template_fname,
               'out5.Rmd']
        code, stdout, stderr = run_command(cmd)
        assert read_file('out5.Rmd') == te.T_SOLUTION_STR
