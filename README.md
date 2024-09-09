<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# antsibull-fileutils -- File Utility Library for Community Ansible Tools
[![Discuss on Matrix at #antsibull:ansible.com](https://img.shields.io/matrix/antsibull:ansible.com.svg?server_fqdn=ansible-accounts.ems.host&label=Discuss%20on%20Matrix%20at%20%23antsibull:ansible.com&logo=matrix)](https://matrix.to/#/#antsibull:ansible.com)
[![Nox badge](https://github.com/ansible-community/antsibull-fileutils/actions/workflows/nox.yml/badge.svg)](https://github.com/ansible-community/antsibull-fileutils/actions/workflows/nox.yml)
[![Codecov badge](https://img.shields.io/codecov/c/github/ansible-community/antsibull-fileutils)](https://codecov.io/gh/ansible-community/antsibull-fileutils)
[![REUSE status](https://api.reuse.software/badge/github.com/ansible-community/antsibull-fileutils)](https://api.reuse.software/info/github.com/ansible-community/antsibull-fileutils)

This library provides file utils needed by community Ansible tooling.

You can find a list of changes in [the antsibull-fileutils changelog](./CHANGELOG.rst).

Unless otherwise noted in the code, it is licensed under the terms of the GNU
General Public License v3 or, at your option, later.

antsibull-fileutils is covered by the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html).

## Versioning and compatibility

From version 1.0.0 on, antsibull-fileutils sticks to semantic versioning and aims at providing no backwards compatibility breaking changes during a major release cycle. We might make exceptions from this in case of security fixes for vulnerabilities that are severe enough.

The current development version is 1.x.y. 1.x.y is developed on the `main` branch.

## Development

Install and run `nox` to run all tests. That's it for simple contributions!
`nox` will create virtual environments in `.nox` inside the checked out project
and install the requirements needed to run the tests there.

To run specific tests:

1. `nox -e test` to only run unit tests;
2. `nox -e coverage` to display combined coverage results after running `nox -e
   test`;
3. `nox -e lint` to run all linters and formatters at once;
4. `nox -e formatters` to run `isort` and `black`;
3. `nox -e codeqa` to run `flake8`, `pylint`, `reuse lint`, and `antsibull-changelog lint`;
6. `nox -e typing` to run `mypy` and `pyre`

## Creating a new release:

1. Run `nox -e bump -- <version> <release_summary_message>`. This:
   * Bumps the package version in `src/antsibull_fileutils/__init__.py`.
   * Creates `changelogs/fragments/<version>.yml` with a `release_summary` section.
   * Runs `antsibull-changelog release` and adds the changed files to git.
   * Commits with message `Release <version>.` and runs `git tag -a -m 'antsibull-fileutils <version>' <version>`.
   * Runs `hatch build`.
2. Run `git push` to the appropriate remotes.
3. Once CI passes on GitHub, run `nox -e publish`. This:
   * Runs `hatch publish`;
   * Bumps the version to `<version>.post0`;
   * Adds the changed file to git and run `git commit -m 'Post-release version bump.'`;
4. Run `git push --follow-tags` to the appropriate remotes and create a GitHub release.

## License

Unless otherwise noted in the code, it is licensed under the terms of the GNU
General Public License v3 or, at your option, later. See
[LICENSES/GPL-3.0-or-later.txt](https://github.com/ansible-community/antsibull-fileutils/tree/main/LICENSE)
for a copy of the license.

The repository follows the [REUSE Specification](https://reuse.software/spec/) for declaring copyright and
licensing information. The only exception are changelog fragments in ``changelog/fragments/``.
