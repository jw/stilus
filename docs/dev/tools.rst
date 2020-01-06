Tools
=====

Some handy tools when you're developing Stilus.

Sphinx
------

To create the latest documentation:

`$ poetry run sphinx-build -b html docs build/html`

pre-commit
----------

After installing pre-commit, all the hooks will run automatically
after each commit.  These hooks will run black on the changed files.

Deploy
------

To deploy, update the version first.  Let's say version x.y.z...

`$ vim stilus/__version__.py  # change the VERSION to (x, y, z)`

`$ poetry version x.y.z`

And commit to the repo:

`$ git commit -m 'Bumped the version'`

`$ git push`

(This will ensure proper blacking of the code.)

Then create a tag:

`$ git tag -a x.y.z -m 'x.y.z'`

`$ git push --follow-tag`

Then publish to Pypi:

`$ poetry publish`
