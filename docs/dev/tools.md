## Tools

### Sphinx

poetry run sphinx-build -b html docs build/html

### Deploy

First:

git commit
git push

This will ensure proper blacking of the code.

git tag -a 2.1.0 -m "Version bump."
poetry publish 
