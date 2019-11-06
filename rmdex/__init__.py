""" Initialize rmdex package
"""

# Versioneer boilerplate
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


from .exerciser import make_exercise, make_solution, check_marks
