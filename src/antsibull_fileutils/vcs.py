# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024, Ansible Project

"""
Git functions.
"""

from __future__ import annotations

import subprocess
import typing as t

if t.TYPE_CHECKING:
    from _typeshed import StrPath


def detect_vcs(
    path: StrPath,
    *,
    git_bin_path: StrPath = "git",
    log_debug: t.Callable[[str], None] | None = None,
    log_info: t.Callable[[str], None] | None = None,
) -> t.Literal["none", "git"]:
    """
    Try to detect whether the given ``path`` is part of a VCS repository.

    NOTE: The return type might be extended in the future. To be on the safe
          side, test for the types you support, and use a fallback for unknown
          values (treat them like ``"none"``).
    """

    def do_log_debug(msg: str, *args: t.Any) -> None:
        if log_debug:
            log_debug(msg, *args)

    def do_log_info(msg: str, *args: t.Any) -> None:
        if log_info:
            log_info(msg, *args)

    do_log_debug("Trying to determine whether {!r} is a Git repository", path)
    try:
        result = subprocess.check_output(
            [str(git_bin_path), "-C", path, "rev-parse", "--is-inside-work-tree"],
            text=True,
            encoding="utf-8",
        ).strip()
        do_log_debug("Git output: {}", result)
        if result == "true":
            do_log_info("Identified {!r} as a Git repository", path)
            return "git"
    except subprocess.CalledProcessError as exc:
        # This is likely not inside a work tree
        do_log_debug("Git failed: {}", exc)
    except FileNotFoundError as exc:
        # Cannot find git executable
        do_log_debug("Cannot find git: {}", exc)

    # Fallback: no VCS detected
    do_log_debug("Cannot identify VCS")
    return "none"


def list_git_files(
    directory: StrPath,
    *,
    git_bin_path: StrPath = "git",
    log_debug: t.Callable[[str], None] | None = None,
) -> list[bytes]:
    """
    List all files not ignored by git in a directory and subdirectories.

    Raises ``ValueError`` in case of errors.
    """

    def do_log_debug(msg: str, *args) -> None:
        if log_debug:
            log_debug(msg, *args)

    do_log_debug("Identifying files not ignored by Git in {!r}", directory)
    try:
        result = subprocess.check_output(
            [
                str(git_bin_path),
                "ls-files",
                "-z",
                "--cached",
                "--others",
                "--exclude-standard",
                "--deduplicate",
            ],
            cwd=directory,
        ).strip(b"\x00")
        if result == b"":
            return []
        return result.split(b"\x00")
    except subprocess.CalledProcessError as exc:
        raise ValueError("Error while running git") from exc
    except FileNotFoundError as exc:
        raise ValueError("Cannot find git executable") from exc
