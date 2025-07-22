# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025, Ansible Project

"""
Test tempfile module.
"""

from __future__ import annotations

import contextlib
import os
import pathlib
import re
from pathlib import Path
from unittest import mock

import pytest

from antsibull_fileutils.tempfile import (
    TemporaryDirectoryHelper,
    find_tempdir,
    is_acceptable_tempdir,
)


@pytest.mark.parametrize(
    "directory, expected",
    [
        ("/", True),
        ("/ansible_collections", False),
        ("/ansible_collections/foo", False),
        ("/ansible_collections/foo/bar", False),
        ("/foo/ansible_collections", False),
        ("/foo/bar/ansible_collections", False),
        ("/foo/ansible_collections/bar", False),
        ("/foo/bar/ansible_collections/baz/bam", False),
        ("/foo/bar/baz/bam", True),
    ],
)
def test_is_acceptable_tempdir(directory: str, expected: bool) -> None:
    assert is_acceptable_tempdir(Path(directory)) == expected


def set_env_var_value(env_var: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(env_var, None)
    else:
        os.environ[env_var] = value


@contextlib.contextmanager
def set_env_var(env_var: str, value: str | None):
    current_value = os.environ.get(env_var)
    try:
        set_env_var_value(env_var, value)
        yield
    finally:
        set_env_var_value(env_var, current_value)


def test_find_tempdir(tmp_path: Path) -> None:
    random_dirname = "fooThaequie4QuaP3tie"

    def is_acceptable(path: Path) -> bool:
        print(path)
        if path.name == random_dirname:
            return True
        for parent in path.parents:
            if parent.name == random_dirname:
                return True
        return False

    random_dir = tmp_path / random_dirname / "bar"
    random_dir.mkdir(parents=True)
    with set_env_var("ANTSIBULL_FILEUTILS_TMPDIR", str(random_dir)):
        print(os.environ)
        assert find_tempdir(is_acceptable) == random_dir

    with set_env_var("ANTSIBULL_FILEUTILS_TMPDIR", None):
        with pytest.raises(ValueError):
            find_tempdir(is_acceptable)

    with pytest.raises(ValueError):
        find_tempdir(lambda path: False)


def test_TemporaryDirectoryHelper(tmp_path_factory) -> None:
    temp: Path = tmp_path_factory.mktemp("temp")

    assert temp.is_dir()
    tdh = TemporaryDirectoryHelper(directory=temp)
    assert tdh.name == temp
    with tdh:
        assert temp.is_dir()
        assert tdh.name == temp
    assert not temp.exists()
    assert not temp.is_dir()
    assert tdh.name == temp

    temp.mkdir()
    assert temp.is_dir()
    with TemporaryDirectoryHelper(directory=temp):
        assert temp.is_dir()
        temp.rmdir()
    assert not temp.exists()
    assert not temp.is_dir()

    temp.mkdir()
    assert temp.is_dir()
    with TemporaryDirectoryHelper(directory=temp, delete=False):
        assert temp.is_dir()
    assert temp.is_dir()

    assert temp.is_dir()
    with TemporaryDirectoryHelper(directory=temp, delete=False):
        assert temp.is_dir()
        temp.rmdir()
    assert not temp.exists()
    assert not temp.is_dir()
