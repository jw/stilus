# Stilus contributing guidelines

Thank you for wanting to contribute to Stilus!

## Maintainers

The current developer of Stylus is me, Jan Willems 
([@jw](https://github.com/jw)),

Do not hesitate to ask me any questions or give me any remarks regarding this
project.

## Code of Conduct

Please note that this project is released with a 
[Contributor Code of Conduct](code_of_conduct.md). By participating in this 
project you agree to abide by its terms.

## How you can help

You're welcome to:

- send pull requests;
- report bugs;
- ask questions;
- fix existing issues;
- suggest new features and enhancements;
- write, rewrite, fix and enhance docs;
- contribute in other ways if you'd like.

### Pull-requests

If you fixed or added something useful to the project, you can send a 
pull-request. It will be reviewed by a maintainer and accepted, or commented 
for rework, or declined.

#### Before submitting a PR:

1. Make sure you have tests for your modifications.
2. Run python setup test locally to catch any errors.
3. Also run a flake8 check.

#### Why did you close my pull request or issue?

Nothing is worse than a project with hundreds of stale issues. To keep 
things orderly, I'll try to close/resolve issues as quickly as possible.

#### PR/Issue closing criteria

We'll close your PR or issue if:

1. It's a duplicate of an existing issue.
2. Outside of the scope of the project.
3. The bug is not reproducible.
4. You are unresponsive after a few days.
5. The feature request introduces too much complexity (or too many edge cases) to the tool
    - We weigh a request's complexity with the value it brings to the community.

Please do not take offense if your ticket is closed. I'm only trying to keep 
the number of issues manageable.

### Filing bugs

If you found an error, typo, or any other flaw in the project, please report 
it using [GitHub Issues](https://github.com/jw/stilus/issues). Try searching 
the issues to see if there is an existing report of your bug, and if you'd 
find it, you could bump it by adding your test case there.

When it comes to bugs, the more details you provide, the easier it is to 
reproduce the issue and the faster it could be fixed.

The best case would be if you'd provide a minimal reproducible test case 
illustrating a bug. For most cases just a code snippet would be enough, 
for more complex cases you can create gists or even test repos on GitHub — 
we would be glad to look into any problems you'll have with Stylus.

### Asking questions

GitHub issues is not the best place for asking questions like “why my code 
won't work” or “is there a way to do X in Stilus”, but I will add a 'Stilus'
tag to the stackoverfow site.

### Fixing existing issues

If you'd like to work on an existing issue, just leave a comment on the issue 
saying that you'll work on a PR fixing it.

### Proposing features

If you've got an idea for a new feature, file an issue providing some details 
on your idea. Try searching the issues to see if there is an existing proposal 
for your feature and feel free to bump it by providing your use case or 
explaining why this feature is important for you.

We should note that not everything should be done as a “Stylus feature”, 
some features better be a Stilus plug-ins, some could be much faster 
implemented using a post-processor, some are just not in the scope of the 
project.

