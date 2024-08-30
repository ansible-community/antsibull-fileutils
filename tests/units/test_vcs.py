# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project

"""
Test utils module.
"""

from __future__ import annotations

import subprocess
from unittest import mock

import pytest

from antsibull_fileutils.vcs import detect_vcs


def test_detect_vcs():
    path = "/path/to/dir"
    git_bin_path = "/path/to/git"
    git_command = [git_bin_path, "-C", path, "rev-parse", "--is-inside-work-tree"]

    def collect_log():
        debug = []
        info = []

        def log_debug(msg: str, *args) -> None:
            debug.append((msg, args))

        def log_info(msg: str, *args) -> None:
            info.append((msg, args))

        return (
            {
                "log_debug": log_debug,
                "log_info": log_info,
            },
            debug,
            info,
        )

    with mock.patch(
        "subprocess.check_output",
        return_value="true\n",
    ) as m:
        kwargs, debug, info = collect_log()
        assert detect_vcs(path, git_bin_path=git_bin_path, **kwargs) == "git"
        m.assert_called_with(git_command, text=True, encoding="utf-8")
        assert debug == [
            ("Trying to determine whether {!r} is a Git repository", ("/path/to/dir",)),
            ("Git output: {}", ("true",)),
        ]
        assert info == [
            ("Identified {!r} as a Git repository", ("/path/to/dir",)),
        ]

    with mock.patch(
        "subprocess.check_output",
        return_value="true\n",
    ) as m:
        assert detect_vcs(path, git_bin_path=git_bin_path) == "git"
        m.assert_called_with(git_command, text=True, encoding="utf-8")

    with mock.patch(
        "subprocess.check_output",
        return_value="foobar\n".encode("utf-8"),
    ) as m:
        assert detect_vcs(path, git_bin_path=git_bin_path) == "none"
        m.assert_called_with(git_command, text=True, encoding="utf-8")

    with mock.patch(
        "subprocess.check_output",
        side_effect=subprocess.CalledProcessError(128, path),
    ) as m:
        assert detect_vcs(path, git_bin_path=git_bin_path) == "none"
        m.assert_called_with(git_command, text=True, encoding="utf-8")

    with mock.patch(
        "subprocess.check_output",
        side_effect=FileNotFoundError(),
    ) as m:
        assert detect_vcs(path, git_bin_path=git_bin_path) == "none"
        m.assert_called_with(git_command, text=True, encoding="utf-8")
