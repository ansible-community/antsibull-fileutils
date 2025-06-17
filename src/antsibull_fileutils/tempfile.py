# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025, Ansible Project

"""
Ansible-friendly temporary directories.
"""

from __future__ import annotations

import functools
import os
import shutil
import tempfile
import types
import typing as t
from pathlib import Path


def _get_tempdir_proposals() -> t.Generator[Path]:
    yield Path(tempfile.gettempdir())
    for env_var in ("ANTSIBULL_FILEUTILS_TMPDIR",):
        if os.environ.get(env_var):
            yield Path(os.environ[env_var])
    # Try OS specific locations (we stick to *nix systems here):
    yield Path("/tmp")
    yield Path("/var/tmp")
    yield Path("/usr/tmp")
    # Last resort:
    yield Path.cwd()


def _is_acceptable_tempdir(directory: Path) -> bool:
    if directory.name == "ansible_collections":
        return False
    for parent in directory.parents:
        if parent.name == "ansible_collections":
            return False
    return True


@functools.cache
def _get_tempdir() -> Path:
    for path in _get_tempdir_proposals():
        if not path.is_dir():
            continue
        directory = path.absolute()
        if _is_acceptable_tempdir(directory):
            return directory
    candidates = ", ".join([str(path) for path in _get_tempdir_proposals()])
    raise ValueError(
        f"Cannot find ansible-friendly temporary directory! Candidates: {candidates}"
    )


def ansible_mkdtemp(*, suffix: str | None = None, prefix: str | None = None) -> Path:
    """
    Create a temporary directory that is guaranteed
    not to be inside an ``ansible_collections`` tree.

    The ``suffix`` and ``prefix`` directories behave as for ``tempfile.mkdtemp()``.
    Will raise ``ValueError`` if no temporary directory can be found.
    This can only happen if places like ``/tmp``, ``/var/tmp``, and ``/usr/tmp``
    all do not exist.
    """
    result = Path(tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=_get_tempdir()))
    if not _is_acceptable_tempdir(result):
        # Clean up before erroring out
        try:
            result.unlink(missing_ok=True)
        except:  # noqa: E722 # pylint: disable=bare-except
            pass
        raise ValueError(f"Internal error: got invalid temp directory {result}")
    return result


class AnsibleTemporaryDirectory:
    def __init__(
        self,
        *,
        suffix: str | None = None,
        prefix: str | None = None,
        ignore_cleanup_errors: bool = False,
        delete: bool = True,
    ) -> None:
        """
        Create a temporary directory and provide it as a context manager.

        Note that opposed to ``tempfile.TemporaryDirectory``, no finalizer is registered
        that will clean up the temporary directory if garbage collector cleans up the
        class before ``__exit__()`` was called.
        """
        self._ignore_cleanup_errors = ignore_cleanup_errors
        self._delete = delete
        self._directory = ansible_mkdtemp(suffix=suffix, prefix=prefix)

    @property
    def name(self) -> Path:
        """
        Return the temporary directory.
        """
        return self._directory

    def cleanup(self) -> None:
        """
        Remove temporary directory.
        """
        if not self._directory.exists():
            return
        shutil.rmtree(self._directory, ignore_errors=self._ignore_cleanup_errors)

    def __enter__(self) -> Path:
        return self._directory

    def __exit__(
        self,
        exc_type: t.Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> t.Literal[False]:
        if self._delete:
            self.cleanup()
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name!r}>"


__all__ = ("ansible_mkdtemp", "AnsibleTemporaryDirectory")
