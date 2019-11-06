# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test scripts

Test running scripts
"""

from os.path import abspath

from scripttester import ScriptTester

from rnbgrader.tmpdirs import in_dtemp

from .test_exerciser import SOLUTION_FNAME, EXERCISE_STR


runner = ScriptTester('rmdex', win_bin_ext='.exe')
run_command = runner.run_command


def script_test(func):
    # Decorator to label test as a script_test
    func.script_test = True
    return func



@script_test
def test_rmdex_check():
    with in_dtemp():
        cmd = ['rmdex_check', abspath(SOLUTION_FNAME), 'out.Rmd']
        code, stdout, stderr = run_command(cmd)
        with open('out.Rmd') as fobj:
            contents = fobj.read()
        assert contents == EXERCISE_STR
        cmd = ['rmdex_check', '--check-marks', abspath(SOLUTION_FNAME),
               'out2.Rmd']
        code, stdout, stderr = run_command(cmd)
        with open('out2.Rmd') as fobj:
            contents = fobj.read()
        assert contents == EXERCISE_STR
