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

from antsibull_fileutils.copier import (
    CollectionCopier,
    Copier,
    CopierError,
    GitCopier,
    _is_internal,
)

from .utils import collect_log


@pytest.mark.parametrize(
    "directory, link, expected",
    [
        ("", "foo", True),
        ("", "foo/bar", True),
        ("", "foo/../bar", True),
        ("", "foo/../../bar", False),
        ("", "..", False),
        ("", "../foo/bar", False),
        ("foo", ".", True),
        ("foo", "bar", True),
        ("foo", "../bar", True),
        ("foo", "../../bar", False),
        ("foo", "..", True),
    ],
)
def test__is_internal(directory, link, expected):
    assert _is_internal(directory, link) == expected


def assert_same(
    a: pathlib.Path, b: pathlib.Path, *, changed_link: str | None = None
) -> None:
    if a.is_symlink():
        assert b.is_symlink()
        assert (changed_link or a.readlink()) == b.readlink()
        return
    assert not b.is_symlink()
    if a.is_file():
        assert b.is_file()
        assert a.read_bytes() == b.read_bytes()
        return
    if a.is_dir():
        assert b.is_dir()
        return


def assert_same_recursively(a: pathlib.Path, b: pathlib.Path) -> None:
    assert a.is_dir()
    assert b.is_dir()
    dest = {f.name: f for f in b.iterdir()}
    for f in a.iterdir():
        f_other = dest.pop(f.name)
        assert_same(f, f_other)
        if f.is_dir():
            assert_same_recursively(f, f_other)
    assert dest == {}


def test_copier(tmp_path_factory):
    directory: pathlib.Path = tmp_path_factory.mktemp("copier")

    src_dir = directory / "src"
    src_dir.mkdir()
    (src_dir / "empty").touch()
    (src_dir / "link").symlink_to("empty")
    (src_dir / "dir").mkdir()
    (src_dir / "file").write_text("content", encoding="utf-8")
    (src_dir / "dir" / "binary_file").write_bytes(b"\x00\x01\x02")
    (src_dir / "dir" / "another_file").write_text("more", encoding="utf-8")

    dest_dir = directory / "dest1"
    copier = Copier()
    copier.copy(str(src_dir), str(dest_dir))
    assert_same_recursively(src_dir, dest_dir)

    def src_dst(*appendix):
        s = src_dir
        d = dest_dir
        for a in appendix:
            s = s / a
            d = d / a
        return str(s), str(d)

    dest_dir = directory / "dest2"
    kwargs, debug, info = collect_log(with_info=False)
    copier = Copier(**kwargs)
    copier.copy(
        str(src_dir),
        str(dest_dir),
    )
    assert_same_recursively(src_dir, dest_dir)
    assert sorted(debug) == [
        (
            "Copying complete directory from {!r} to {!r}",
            (str(src_dir), str(dest_dir)),
        ),
        (
            "Copying directory {!r} to {!r}",
            src_dst("dir"),
        ),
        (
            "Copying file {!r} to {!r}",
            src_dst("dir", "another_file"),
        ),
        (
            "Copying file {!r} to {!r}",
            src_dst("dir", "binary_file"),
        ),
        (
            "Copying file {!r} to {!r}",
            src_dst("empty"),
        ),
        (
            "Copying file {!r} to {!r}",
            src_dst("file"),
        ),
        (
            "Copying symlink {!r} to {!r}",
            src_dst("link"),
        ),
    ]

    dest_dir = directory / "dest3"
    kwargs, debug, info = collect_log(with_info=False)
    copier = Copier(**kwargs)
    copier.copy(src_dir, dest_dir)
    assert_same_recursively(src_dir, dest_dir)
    assert sorted(debug) == [
        ("Copying complete directory from {!r} to {!r}", (src_dir, dest_dir)),
        (
            "Copying directory {!r} to {!r}",
            src_dst("dir"),
        ),
        (
            "Copying file {!r} to {!r}",
            src_dst("dir", "another_file"),
        ),
        (
            "Copying file {!r} to {!r}",
            src_dst("dir", "binary_file"),
        ),
        (
            "Copying file {!r} to {!r}",
            src_dst("empty"),
        ),
        (
            "Copying file {!r} to {!r}",
            src_dst("file"),
        ),
        (
            "Copying symlink {!r} to {!r}",
            src_dst("link"),
        ),
    ]

    dest_dir = directory / "dest4"
    kwargs, debug, info = collect_log(with_info=False)
    copier = Copier(**kwargs)
    copier.copy(src_dir, dest_dir, exclude_root=["does-not-exist", "dir", "file"])
    assert sorted(debug) == [
        ("Copying complete directory from {!r} to {!r}", (src_dir, dest_dir)),
        (
            "Copying file {!r} to {!r}",
            src_dst("empty"),
        ),
        (
            "Copying symlink {!r} to {!r}",
            src_dst("link"),
        ),
    ]


def test_git_copier(tmp_path_factory):
    directory: pathlib.Path = tmp_path_factory.mktemp("git-copier")

    (directory / "other").write_bytes(b"other")
    (directory / "other_dir").mkdir()
    (directory / "other_dir" / "file").write_bytes(b"foo")

    src_dir = directory / "src"
    src_dir.mkdir()
    (src_dir / "empty").touch()
    (src_dir / "link").symlink_to("empty")
    (src_dir / "link_dir").symlink_to("dir")
    (src_dir / "trick_link").symlink_to("../src/empty")
    (src_dir / "out_link").symlink_to("../other")
    (src_dir / "out_link_dir").symlink_to("../other_dir")
    (src_dir / "abs_link").symlink_to(str((src_dir / "link").resolve()))
    (src_dir / "dead_link").symlink_to("does-not-exist")
    (src_dir / "out_dead_link").symlink_to("../does-not-exist")
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

    def src_dst(*appendix):
        s = src_dir
        d = dest_dir
        for a in appendix:
            s = s / a
            d = d / a
        return str(s), str(d)

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
            ("Copying symlink {!r} to {!r}", src_dst("link")),
            ("Copying directory {!r} to {!r}", src_dst("dir")),
            ("Copying file {!r} to {!r}", src_dst("dir", "binary_file")),
            ("Copying file {!r} to {!r}", src_dst("dir", "another_file")),
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

    dest_dir = directory / "dest3"
    with mock.patch(
        "antsibull_fileutils.copier.list_git_files",
        return_value=[
            b"link_dir",
            b"trick_link",
            b"out_link",
            b"out_link_dir",
            b"abs_link",
            b"dead_link",
        ],
    ) as m:
        copier = GitCopier(git_bin_path="/path/to/git", normalize_links=False)
        copier.copy(str(src_dir), str(dest_dir))
        m.assert_called_with(str(src_dir), git_bin_path="/path/to/git", log_debug=None)
        assert dest_dir.is_dir()
        assert {p.name for p in dest_dir.iterdir()} == {
            "link_dir",
            "trick_link",
            "out_link",
            "out_link_dir",
            "abs_link",
            "dead_link",
        }
        assert_same(src_dir / "link_dir", dest_dir / "link_dir")
        assert_same((src_dir / "trick_link").resolve(), dest_dir / "trick_link")
        assert_same((src_dir / "out_link").resolve(), dest_dir / "out_link")
        assert_same_recursively(
            (src_dir / "out_link_dir").resolve(), dest_dir / "out_link_dir"
        )
        assert_same((src_dir / "abs_link").resolve(), dest_dir / "abs_link")
        assert_same(src_dir / "dead_dir", dest_dir / "dead_dir")

    dest_dir = directory / "dest4"
    with mock.patch(
        "antsibull_fileutils.copier.list_git_files",
        return_value=[
            b"link_dir",
            b"trick_link",
            b"out_link",
            b"out_link_dir",
            b"abs_link",
            b"dead_link",
        ],
    ) as m:
        copier = GitCopier(git_bin_path="/path/to/git")
        copier.copy(str(src_dir), str(dest_dir))
        m.assert_called_with(str(src_dir), git_bin_path="/path/to/git", log_debug=None)
        assert dest_dir.is_dir()
        assert {p.name for p in dest_dir.iterdir()} == {
            "link_dir",
            "trick_link",
            "out_link",
            "out_link_dir",
            "abs_link",
            "dead_link",
        }
        assert_same(src_dir / "link_dir", dest_dir / "link_dir")
        assert_same(
            src_dir / "trick_link",
            dest_dir / "trick_link",
            changed_link=pathlib.Path("empty"),
        )
        assert_same((src_dir / "out_link").resolve(), dest_dir / "out_link")
        assert_same_recursively(
            (src_dir / "out_link_dir").resolve(), dest_dir / "out_link_dir"
        )
        assert_same(
            src_dir / "abs_link",
            dest_dir / "abs_link",
            changed_link=pathlib.Path("empty"),
        )
        assert_same(src_dir / "dead_dir", dest_dir / "dead_dir")

    def src_dst(*appendix):
        s = src_dir
        d = dest_dir
        for a in appendix:
            s = s / a
            d = d / a
        return str(s), str(d)

    dest_dir = directory / "dest5"
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

    dest_dir = directory / "dest6"
    with mock.patch(
        "antsibull_fileutils.copier.list_git_files",
        return_value=[
            b"out_dead_link",
        ],
    ) as m:
        copier = GitCopier(git_bin_path="/path/to/git")
        with pytest.raises(FileNotFoundError) as exc:
            copier.copy(str(src_dir), str(dest_dir))
        m.assert_called_with(str(src_dir), git_bin_path="/path/to/git", log_debug=None)

    dest_dir = directory / "dest7"
    with mock.patch(
        "antsibull_fileutils.copier.list_git_files",
        return_value=[b"link", b"foobar", b"dir/binary_file", b"dir/another_file"],
    ) as m:
        kwargs, debug, info = collect_log(with_info=False)
        copier = GitCopier(git_bin_path="/path/to/git", **kwargs)
        copier.copy(src_dir, dest_dir, exclude_root=["does-not-exist", "link", "dir"])
        m.assert_called_with(src_dir, git_bin_path="/path/to/git", **kwargs)

        assert debug == [
            ("Identifying files not ignored by Git in {!r}", (src_dir,)),
            ("Copying {} file(s) from {!r} to {!r}", (4, src_dir, dest_dir)),
        ]
        assert dest_dir.is_dir()
        assert {p.name for p in dest_dir.iterdir()} == set()


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
