""" Initialize rmdex package
"""

# Versioneer boilerplate
from . import _version
__version__ = _version.get_versions()['version']


from .exerciser import make_exercise, make_solution, check_marks
