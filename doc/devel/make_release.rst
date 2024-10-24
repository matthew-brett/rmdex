###############
Releasing Rmdex
###############

* Review the open list of `rmdex issues`_.  Check whether there are
  outstanding issues that can be closed, and whether there are any issues that
  should delay the release.  Label them.

* Review and update the release notes.  Review and update the :file:`Changelog`
  file.  Get a partial list of contributors with something like::

      git log 0.2.0.. | grep '^Author' | cut -d' ' -f 2- | sort | uniq

  where ``0.2.0`` was the last release tag name.

  Then manually go over ``git shortlog 0.2.0..`` to make sure the release notes
  are as complete as possible and that every contributor was recognized.

* Use the opportunity to update the ``.mailmap`` file if there are any
  duplicate authors listed from ``git shortlog -ns``.

* Check the copyright years in ``doc/conf.py`` and ``LICENSE``;

* Check the output of::

    rst2html.py README.rst > ~/tmp/readme.html

  because this will be the output used by PyPi_

* Check `rmdex travis-ci`_.

* Once everything looks good, you are ready to upload the source release to
  PyPi.  See `setuptools intro`_.  Make sure you have a file
  ``\$HOME/.pypirc``, of form::

    [distutils]
    index-servers =
        pypi

    [pypi]
    repository: https://upload.pypi.io/legacy/
    username:your.pypi.username
    password:your-password

* Once everything looks good, edit the version number in `rmdex/__init__.py`,
  and tag the release::

    git tag -s 0.3

* Clean::

    # Check no files outside version control that you want to keep
    git status
    # Nuke
    git clean -fxd

* When ready::

    pip install build twine
    python -m build --sdist
    twine upload dist/rmdex*tar.gz

* Upload the release commit and tag to github::

    git push
    git push --tags

* Push the docs to github pages with::

    cd doc
    make github

* Update the version number to an alpha again.

.. include:: ../links_names.inc
