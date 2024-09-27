# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024, Ansible Project

"""
Directory and collection copying helpers.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import typing as t

from antsibull_fileutils.vcs import list_git_files

if t.TYPE_CHECKING:
    from _typeshed import StrPath


class CopierError(Exception):
    pass


class Copier:
    """
    Allows to copy directories.
    """

    def __init__(self, *, log_debug: t.Callable[[str], None] | None = None):
        self._log_debug = log_debug

    def _do_log_debug(self, msg: str, *args: t.Any) -> None:
        if self._log_debug:
            self._log_debug(msg, *args)

    def copy(self, from_path: StrPath, to_path: StrPath) -> None:
        """
        Copy a directory ``from_path`` to a destination ``to_path``.

        ``to_path`` must not exist, but its parent directory must exist.
        """
        self._do_log_debug(
            "Copying complete directory from {!r} to {!r}", from_path, to_path
        )
        shutil.copytree(from_path, to_path, symlinks=True)


class GitCopier(Copier):
    """
    Allows to copy directories that are part of a Git repository.
    """

    def __init__(
        self,
        *,
        git_bin_path: StrPath = "git",
        log_debug: t.Callable[[str], None] | None = None,
    ):
        super().__init__(log_debug=log_debug)
        self.git_bin_path = git_bin_path

    def copy(self, from_path: StrPath, to_path: StrPath) -> None:
        self._do_log_debug("Identifying files not ignored by Git in {!r}", from_path)
        try:
            files = list_git_files(
                from_path, git_bin_path=self.git_bin_path, log_debug=self._log_debug
            )
        except ValueError as exc:
            raise CopierError(
                f"Error while listing files not ignored by Git in {from_path}: {exc}"
            ) from exc

        self._do_log_debug(
            "Copying {} file(s) from {!r} to {!r}", len(files), from_path, to_path
        )
        os.mkdir(to_path, mode=0o700)
        created_directories = set()
        for file in files:
            # Decode filename and check whether the file still exists
            # (deleted files are part of the output)
            file_decoded = file.decode("utf-8")
            src_path = os.path.join(from_path, file_decoded)
            if not os.path.exists(src_path):
                continue

            # Check whether the directory for this file exists
            directory, _ = os.path.split(file_decoded)
            if directory not in created_directories:
                os.makedirs(os.path.join(to_path, directory), mode=0o700, exist_ok=True)
                created_directories.add(directory)

            # Copy the file
            dst_path = os.path.join(to_path, file_decoded)
            shutil.copyfile(src_path, dst_path, follow_symlinks=False)


class CollectionCopier:
    """
    Creates a copy of a collection to a place where ``--playbook-dir`` can be used
    to prefer this copy of the collection over any installed ones.
    """

    def __init__(
        self,
        *,
        source_directory: StrPath,
        namespace: str,
        name: str,
        copier: Copier,
        log_debug: t.Callable[[str], None] | None = None,
    ):
        self.source_directory = source_directory
        self.namespace = namespace
        self.name = name
        self.copier = copier
        self._log_debug = log_debug

        self.dir = os.path.realpath(tempfile.mkdtemp(prefix="antsibull-fileutils"))

    def _do_log_debug(self, msg: str, *args: t.Any) -> None:
        if self._log_debug:
            self._log_debug(msg, *args)

    def __enter__(self) -> tuple[str, str]:
        try:
            collection_container_dir = os.path.join(
                self.dir, "collections", "ansible_collections", self.namespace
            )
            os.makedirs(collection_container_dir)

            collection_dir = os.path.join(collection_container_dir, self.name)
            self._do_log_debug("Temporary collection directory: {!r}", collection_dir)

            self.copier.copy(self.source_directory, collection_dir)

            self._do_log_debug("Temporary collection directory has been populated")
            return (
                self.dir,
                collection_dir,
            )
        except Exception:
            shutil.rmtree(self.dir, ignore_errors=True)
            raise

    def __exit__(self, type_, value, traceback_):
        shutil.rmtree(self.dir, ignore_errors=True)
