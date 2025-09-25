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
import typing as t

from antsibull_fileutils.tempfile import ansible_mkdtemp
from antsibull_fileutils.vcs import list_git_files

if t.TYPE_CHECKING:
    from _typeshed import StrPath


class CopierError(Exception):
    pass


def _is_internal(directory: str, link: str) -> bool:
    dest = os.path.join(directory, link)
    if os.path.isabs(dest):
        return False

    if os.path.splitdrive(dest)[0]:
        return False

    normpath = os.path.normpath(dest)
    return not (normpath == ".." or normpath.startswith(".." + os.sep))


class _TreeCopier:
    def __init__(
        self,
        source: StrPath,
        dest: StrPath,
        *,
        keep_inside_symlinks: bool = True,
        keep_outside_symlinks: bool = False,
        normalize_links: bool = True,
        log_debug: t.Callable[[str], None] | None = None,
    ):
        """
        Initialize copy helper
        """
        self._log_debug = log_debug
        self.created_directories: set[str] = {".", ""}
        self.source = source
        self.dest = dest
        self.keep_inside_symlinks = keep_inside_symlinks
        self.keep_outside_symlinks = keep_outside_symlinks
        self.never_keep = not (keep_inside_symlinks or keep_outside_symlinks)
        self.normalize_links = normalize_links
        os.mkdir(self.dest, mode=0o700)

    def _do_log_debug(self, msg: str, *args: t.Any) -> None:
        if self._log_debug:
            self._log_debug(msg, *args)

    def _copy_link(self, directory: str, full_source: str, full_dest: str) -> None:
        link = os.readlink(full_source)
        if self.normalize_links:
            full_directory = os.path.join(self.source, directory)
            link = os.path.relpath(os.path.join(full_directory, link), full_directory)

        internal = False if self.never_keep else _is_internal(directory, link)
        keep = self.keep_inside_symlinks if internal else self.keep_outside_symlinks
        if keep:
            self._do_log_debug("Copying symlink {!r} to {!r}", full_source, full_dest)
            os.symlink(link, full_dest)
            shutil.copystat(full_source, full_dest, follow_symlinks=False)
            return

        real_source = os.path.realpath(full_source)
        if os.path.isdir(real_source):
            self._do_log_debug(
                "Copying symlinked directory tree {!r} to {!r}", full_source, full_dest
            )
            shutil.copytree(real_source, full_dest, symlinks=False)
            return

        self._do_log_debug(
            "Copying symlinked file {!r} to {!r}", full_source, full_dest
        )
        shutil.copy2(real_source, full_dest)

    def _create_dir(self, directory: str) -> None:
        if directory not in self.created_directories:
            src_dir = os.path.join(self.source, directory)
            dest_dir = os.path.join(self.dest, directory)
            self._do_log_debug("Copying directory {!r} to {!r}", src_dir, dest_dir)
            os.makedirs(dest_dir, mode=0o700, exist_ok=True)
            shutil.copystat(src_dir, dest_dir, follow_symlinks=False)
            self.created_directories.add(directory)

    def _copy_file(self, directory: str, relative_path: str) -> None:
        self._create_dir(directory)

        full_source = os.path.join(self.source, relative_path)
        full_dest = os.path.join(self.dest, relative_path)
        if os.path.islink(full_source):
            self._copy_link(directory, full_source, full_dest)
        else:
            self._do_log_debug("Copying file {!r} to {!r}", full_source, full_dest)
            shutil.copy2(full_source, full_dest)

    def copy_file(
        self, relative_path: str, *, ignore_non_existing: bool = False
    ) -> None:
        if ignore_non_existing and not os.path.lexists(
            os.path.join(self.source, relative_path)
        ):
            return
        directory, _ = os.path.split(relative_path)
        self._copy_file(directory, relative_path)

    def walk(self, exclude_root: list[str] | None = None):
        exclude_root_set: set[str] = set(exclude_root or [])
        for root, dirs, files in os.walk(self.source, followlinks=False, topdown=True):
            directory = os.path.relpath(root, self.source)
            if directory == ".":
                directory = ""
            for file in files:
                if file in exclude_root_set:
                    continue
                relative_path = os.path.join(directory, file)
                self._copy_file(directory, relative_path)
            for path in exclude_root_set:
                try:
                    dirs.remove(path)
                except ValueError:
                    pass
            for a_dir in dirs:
                self._create_dir(os.path.join(directory, a_dir))
            exclude_root_set.clear()


class Copier:
    """
    Allows to copy directories.
    """

    def __init__(
        self,
        *,
        normalize_links: bool = True,
        log_debug: t.Callable[[str], None] | None = None,
    ):
        self.normalize_links = normalize_links
        self._log_debug = log_debug

    def _do_log_debug(self, msg: str, *args: t.Any) -> None:
        if self._log_debug:
            self._log_debug(msg, *args)

    def copy(
        self,
        from_path: StrPath,
        to_path: StrPath,
        *,
        exclude_root: list[str] | None = None,
    ) -> None:
        """
        Copy a directory ``from_path`` to a destination ``to_path``.

        ``to_path`` must not exist, but its parent directory must exist.
        """
        self._do_log_debug(
            "Copying complete directory from {!r} to {!r}", from_path, to_path
        )
        _TreeCopier(
            from_path,
            to_path,
            normalize_links=self.normalize_links,
            log_debug=self._log_debug,
        ).walk(exclude_root=exclude_root)


class GitCopier(Copier):
    """
    Allows to copy directories that are part of a Git repository.
    """

    def __init__(
        self,
        *,
        normalize_links: bool = True,
        git_bin_path: StrPath = "git",
        log_debug: t.Callable[[str], None] | None = None,
        copy_repo_structure: bool = False,
    ):
        super().__init__(normalize_links=normalize_links, log_debug=log_debug)
        self.git_bin_path = git_bin_path
        self.copy_repo_structure = copy_repo_structure

    def copy(
        self,
        from_path: StrPath,
        to_path: StrPath,
        *,
        exclude_root: list[str] | None = None,
    ) -> None:
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
        tc = _TreeCopier(
            from_path,
            to_path,
            normalize_links=self.normalize_links,
            log_debug=self._log_debug,
        )
        exclude_root_set = set(exclude_root or [])
        exclude_root_prefixes = [f"{path}/" for path in exclude_root or []]
        for file in files:
            # Decode filename and check whether the file still exists
            # (deleted files are part of the output)
            file_decoded = file.decode("utf-8")
            if file_decoded in exclude_root_set:
                continue
            if any(file_decoded.startswith(prefix) for prefix in exclude_root_prefixes):
                continue
            tc.copy_file(file_decoded, ignore_non_existing=True)
        # Copy .git directory as well if requested
        if self.copy_repo_structure and os.path.isdir(os.path.join(from_path, ".git")):
            _TreeCopier(
                os.path.join(from_path, ".git"),
                os.path.join(to_path, ".git"),
                normalize_links=self.normalize_links,
                log_debug=self._log_debug,
            ).walk()


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

        self.dir = os.path.realpath(ansible_mkdtemp(prefix="antsibull-fileutils"))

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
