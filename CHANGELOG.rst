=================================
antsibull-fileutils Release Notes
=================================

.. contents:: Topics

v1.5.1
======

Release Summary
---------------

Maintenance release.

Minor Changes
-------------

- Declare support for Python 3.14 (https://github.com/ansible-community/antsibull-fileutils/pull/21).

v1.5.0
======

Release Summary
---------------

Feature release.

Minor Changes
-------------

- Allow ``GitCopier`` to copy the repository structure as well, if it is part of the directory that is being copied (https://github.com/ansible-community/antsibull-fileutils/pull/20).

v1.4.0
======

Release Summary
---------------

Feature release.

Minor Changes
-------------

- Extend ``tempfile`` module to make it easier to find customized temporary directories (https://github.com/ansible-community/antsibull-fileutils/pull/18).

v1.3.0
======

Release Summary
---------------

Bugfix and feature release.

Minor Changes
-------------

- Provide utilities ``antsibull_fileutils.tempfile.ansible_mkdtemp()`` and ``antsibull_fileutils.tempfile.AnsibleTemporaryDirectory`` to create temporary directories that are not part of an ``ansible_collections`` tree (https://github.com/ansible-community/antsibull-fileutils/pull/17).

Bugfixes
--------

- Avoid copying collections into temporary directories that are part of an ``ansible_collections`` tree (https://github.com/ansible-community/antsibull-fileutils/pull/17).

v1.2.0
======

Release Summary
---------------

Feature release.

Minor Changes
-------------

- Allow to exclude top-level files and directories when copying trees (https://github.com/ansible-community/antsibull-fileutils/pull/14).

v1.1.0
======

Release Summary
---------------

Bugfix and feature release.

Minor Changes
-------------

- Declare support for Python 3.13 (https://github.com/ansible-community/antsibull-fileutils/pull/10).
- Rewrite ``Copier`` and ``GitCopier`` so that both symlinks outside the tree and symlinks inside the tree are handled more correctly: symlinks inside the tree are kept, while for symlinks outside the tree the content is copied. Symlinks are normalized by default, which makes this behavior similar to ansible-core's behavior in ``ansible-galaxy collection build``. Also copying now tries to preserve metadata (https://github.com/ansible-community/antsibull-fileutils/pull/8).

Bugfixes
--------

- ``CollectionCopier``'s ``source_directory`` argument now accepts ``pathlib.Path`` objects in addition to ``str`` s (https://github.com/ansible-community/antsibull-fileutils/pull/6).

v1.0.1
======

Release Summary
---------------

Bugfix release.

Bugfixes
--------

- Remove accidentally left-in ``print()`` statement in ``antsibull_fileutils.io.write_file()`` (https://github.com/ansible-community/antsibull-fileutils/pull/5).

v1.0.0
======

Release Summary
---------------

Initial release.
