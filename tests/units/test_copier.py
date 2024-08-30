# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024, Ansible Project

"""
Test utils module.
"""

from __future__ import annotations

import os
import pathlib
import re
from unittest import mock

import pytest

from antsibull_fileutils.copier import CollectionCopier, Copier, CopierError, GitCopier

from .utils import collect_log


def assert_same(a: pathlib.Path, b: pathlib.Path) -> None:
    if a.is_file():
        assert b.is_file()
        assert a.read_bytes() == b.read_bytes()
        return
    if a.is_dir():
        assert b.is_dir()
        return
    if a.is_symlink():
        assert b.is_symlink()
        assert a.readlink() == b.readlink()
        return


def test_copier(tmp_path_factory):
    directory: pathlib.Path = tmp_path_factory.mktemp("copier")

    src_dir = directory / "src"
    dest_dir = directory / "dest"

    with mock.patch(
        "antsibull_fileutils.copier.shutil.copytree",
        return_value=None,
    ) as m:
        copier = Copier()
        copier.copy(str(src_dir), str(dest_dir))
        m.assert_called_with(str(src_dir), str(dest_dir), symlinks=True)

    with mock.patch(
        "antsibull_fileutils.copier.shutil.copytree",
        return_value=None,
    ) as m:
        kwargs, debug, info = collect_log(with_info=False)
        copier = Copier(**kwargs)
        copier.copy(str(src_dir), str(dest_dir))
        m.assert_called_with(str(src_dir), str(dest_dir), symlinks=True)
        assert debug == [
            (
                "Copying complete directory from {!r} to {!r}",
                (str(src_dir), str(dest_dir)),
            ),
        ]

    with mock.patch(
        "antsibull_fileutils.copier.shutil.copytree",
        return_value=None,
    ) as m:
        kwargs, debug, info = collect_log(with_info=False)
        copier = Copier(**kwargs)
        copier.copy(src_dir, dest_dir)
        m.assert_called_with(src_dir, dest_dir, symlinks=True)
        assert debug == [
            ("Copying complete directory from {!r} to {!r}", (src_dir, dest_dir)),
        ]


def test_git_copier(tmp_path_factory):
    directory: pathlib.Path = tmp_path_factory.mktemp("git-copier")

    src_dir = directory / "src"
    src_dir.mkdir()
    (src_dir / "empty").touch()
    (src_dir / "link").symlink_to("empty")
    (src_dir / "dir").mkdir()
    (src_dir / "file").write_text("content", encoding="utf-8")
    (src_dir / "dir" / "binary_file").write_bytes(b"\x00\x01\x02")
    (src_dir / "dir" / "another_file").write_text("more", encoding="utf-8")

    dest_dir = directory / "dest1"
    with mock.patch(
        "antsibull_fileutils.copier.list_git_files",
        return_value=[b"file"],
    ) as m:
        copier = GitCopier(git_bin_path="/path/to/git")
        copier.copy(str(src_dir), str(dest_dir))
        m.assert_called_with(str(src_dir), git_bin_path="/path/to/git", log_debug=None)
        assert dest_dir.is_dir()
        assert {p.name for p in dest_dir.iterdir()} == {"file"}
        assert_same(src_dir / "file", dest_dir / "file")

    dest_dir = directory / "dest2"
    with mock.patch(
        "antsibull_fileutils.copier.list_git_files",
        return_value=[b"link", b"foobar", b"dir/binary_file", b"dir/another_file"],
    ) as m:
        kwargs, debug, info = collect_log(with_info=False)
        copier = GitCopier(git_bin_path="/path/to/git", **kwargs)
        copier.copy(src_dir, dest_dir)
        m.assert_called_with(src_dir, git_bin_path="/path/to/git", **kwargs)

        assert debug == [
            ("Identifying files not ignored by Git in {!r}", (src_dir,)),
            ("Copying {} file(s) from {!r} to {!r}", (4, src_dir, dest_dir)),
        ]
        assert dest_dir.is_dir()
        assert {p.name for p in dest_dir.iterdir()} == {"link", "dir"}
        assert_same(src_dir / "link", dest_dir / "link")
        assert_same(src_dir / "dir", dest_dir / "dir")
        assert {p.name for p in (dest_dir / "dir").iterdir()} == {
            "another_file",
            "binary_file",
        }
        assert_same(src_dir / "dir" / "another_file", dest_dir / "dir" / "another_file")
        assert_same(src_dir / "dir" / "binary_file", dest_dir / "dir" / "binary_file")

    dest_dir = directory / "dest2"
    with mock.patch(
        "antsibull_fileutils.copier.list_git_files",
        side_effect=ValueError("nada"),
    ) as m:
        copier = GitCopier(git_bin_path="/path/to/git")
        with pytest.raises(
            CopierError,
            match=f"^Error while listing files not ignored by Git in {re.escape(str(src_dir))}: nada$",
        ) as exc:
            copier.copy(str(src_dir), str(dest_dir))
        m.assert_called_with(str(src_dir), git_bin_path="/path/to/git", log_debug=None)


def test_collection_copier(tmp_path_factory):
    src_dir: pathlib.Path = tmp_path_factory.mktemp("collection-copier")

    copier = mock.MagicMock()

    with CollectionCopier(
        source_directory=src_dir, namespace="foo", name="bar", copier=copier
    ) as (root_dir, collection_dir):
        assert (
            os.path.join(root_dir, "collections", "ansible_collections", "foo", "bar")
            == collection_dir
        )
        assert os.path.exists(root_dir)
        assert os.path.exists(
            os.path.join(root_dir, "collections", "ansible_collections", "foo")
        )
        assert not os.path.exists(collection_dir)  # our mock doesn't create it

    assert not os.path.exists(root_dir)
    copier.copy.assert_called_with(src_dir, collection_dir)


def test_collection_copier_fail():
    copier = mock.MagicMock()
    copier.copy = mock.MagicMock(side_effect=CopierError("boo"))

    kwargs, debug, info = collect_log(with_info=False)

    cc = CollectionCopier(
        source_directory="/foo", namespace="foo", name="bar", copier=copier, **kwargs
    )
    assert os.path.exists(cc.dir)

    with pytest.raises(CopierError, match="^boo$"):
        with cc as (root_dir, collection_dir):
            assert False

    copier.copy.assert_called_with(
        "/foo", os.path.join(cc.dir, "collections", "ansible_collections", "foo", "bar")
    )
    assert not os.path.exists(cc.dir)
    assert debug == [
        (
            "Temporary collection directory: {!r}",
            (os.path.join(cc.dir, "collections", "ansible_collections", "foo", "bar"),),
        )
    ]
