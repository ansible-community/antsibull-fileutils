=================================
antsibull-fileutils Release Notes
=================================

.. contents:: Topics

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
