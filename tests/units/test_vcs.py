# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024, Ansible Project

"""
Test vcs module.
"""

from __future__ import annotations

import subprocess
from unittest import mock

import pytest

from antsibull_fileutils.vcs import detect_vcs, list_git_files

from .utils import collect_log


def test_detect_vcs():
    path = "/path/to/dir"
    git_bin_path = "/path/to/git"
    git_command = [git_bin_path, "-C", path, "rev-parse", "--is-inside-work-tree"]

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


TEST_LIST_GIT_FILES = [
    (b"", [], False),
    (b"", [], True),
    (b"foo\nbar", [b"foo\nbar"], False),
    (b"foo\x00", [b"foo"], True),
    (b"foo\x00bar", [b"foo", b"bar"], True),
    (
        b"link\x00foobar\x00dir/binary_file",
        [b"link", b"foobar", b"dir/binary_file"],
        False,
    ),
]


@pytest.mark.parametrize("stdout, expected, with_logging", TEST_LIST_GIT_FILES)
def test_list_git_files(stdout: bytes, expected: list[str], with_logging: bool):
    path = "/path/to/dir"
    git_bin_path = "/path/to/git"
    git_command = [
        git_bin_path,
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
        "--deduplicate",
    ]

    with mock.patch(
        "subprocess.check_output",
        return_value=stdout,
    ) as m:
        kwargs, debug, info = collect_log(with_debug=with_logging, with_info=False)
        assert list_git_files(path, git_bin_path=git_bin_path, **kwargs) == expected
        m.assert_called_with(git_command, cwd=path)
        if with_logging:
            assert debug == [("Identifying files not ignored by Git in {!r}", (path,))]


def test_list_git_files_fail():
    path = "/path/to/dir"
    git_bin_path = "/path/to/git"
    git_command = [
        git_bin_path,
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
        "--deduplicate",
    ]

    with mock.patch(
        "subprocess.check_output",
        side_effect=subprocess.CalledProcessError(128, path),
    ) as m:
        with pytest.raises(ValueError, match="^Error while running git$") as exc:
            list_git_files(path, git_bin_path=git_bin_path)

    with mock.patch(
        "subprocess.check_output",
        side_effect=FileNotFoundError(),
    ) as m:
        with pytest.raises(ValueError, match="^Cannot find git executable$") as exc:
            list_git_files(path, git_bin_path=git_bin_path)
