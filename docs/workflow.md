## Workflow

This section describes the workflow we use for Stilus releases, the naming of 
the branches and the meaning behind them.

### Branches

#### Permanent branches

The `master` branch should always be there. Do not fork it directly, 
always create a new branch for your Pull Requests.

A tag is created for each release.  The tags use semantic versioning; see [semver](http://semver.org).

#### Temporarily branches

- `issue-NNN`. If you're working on a fix for an issue, you can use this naming. This would make it easy to understand which issue is affected by your code. You can optionally include a postfix with a short description of the problem, for example `issue-1289-broken-mqs`.

- `feature-…`. Any new feature should be initially be a feature-branch. Such branches won't be merged into the `master` branches directly. The naming would work basically the same as the `issue-…`, but you can omit the issue's number as there couldn't be one issue covering the feature, or you're working on some refactoring.

- `rc-…`. Any new feature release should be at first compiled into a release candidate branch. For example, `rc-0.43` would be a branch for a coming `0.43.0` release. We would merge feature branches and Pull Requests that add new features to the rc-branch, then we test all the changes together, writing tests and docs for those new features and when everything is ready, we increase the version number in `package.json`, then merge the rc-branch into `dev` and `master`.

### Releasing workflow

We follow [semver](http://semver.org/). We're in `0.x` at the moment, however, as Stilus is already widely used, we don't introduce backwards-incompatible changes to our minor releases.

Each minor release should be first compiled into `rc-`branch. Minor release *should not* have fixes in it, as patch-release should be published before a minor one if there are fixes. This would deliver the fixes to the people using the fixed minor, but `x` at patch version.

Patch releases don't need their own `rc` branches, as they could be released from the `dev` branch. 

### Adding tests

First you want to make sure to run the below commands

```
python setup.py test
```

and add tests as fit.
