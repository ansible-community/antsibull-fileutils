# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

from __future__ import annotations

from io import BytesIO

import pytest

from antsibull_fileutils.io import copy_file, read_file, write_file


@pytest.mark.asyncio
async def test_copy_file(tmp_path):
    content = "foo\x00bar\x00baz\x00çäø☺".encode("utf-8")
    content_len = len(content)

    alt_content = "boo\x00bar\x00baz\x00çäø☺".encode("utf-8")
    alt_content_len = "foo\x00bar".encode("utf-8")

    src_path = tmp_path / "file-src"
    src_path.write_bytes(content)

    dst_path = tmp_path / "file-dst"
    assert await copy_file(src_path, dst_path, chunksize=4) is True
    assert dst_path.read_bytes() == content

    assert (
        await copy_file(
            src_path, dst_path, chunksize=4, file_check_content=content_len - 1
        )
        is True
    )
    assert dst_path.read_bytes() == content

    assert (
        await copy_file(src_path, dst_path, chunksize=4, file_check_content=content_len)
        is False
    )
    assert dst_path.read_bytes() == content

    src_path.write_bytes(alt_content)

    assert (
        await copy_file(src_path, dst_path, chunksize=4, file_check_content=content_len)
        is True
    )
    assert dst_path.read_bytes() == alt_content

    src_path.write_bytes(alt_content_len)

    assert (
        await copy_file(src_path, dst_path, chunksize=4, file_check_content=content_len)
        is True
    )
    assert dst_path.read_bytes() == alt_content_len

    dst_path = tmp_path / "file-dst-2"
    assert (
        await copy_file(src_path, dst_path, chunksize=4, file_check_content=content_len)
        is True
    )
    assert dst_path.read_bytes() == alt_content_len


@pytest.mark.asyncio
async def test_read_file(tmp_path):
    content = "foo\x00bar\x00baz\x00çäø☺"
    filename = tmp_path / "file"
    filename.write_text(content, encoding="utf-8")

    assert await read_file(filename, encoding="utf-8") == content
    assert await read_file(str(filename), encoding="utf-8") == content
    assert await read_file(str(filename).encode("utf-8"), encoding="utf-8") == content
    assert await read_file(str(filename).encode("utf-8"), encoding="utf-8") == content

    filename.write_text(content, encoding="utf-16")

    assert await read_file(filename, encoding="utf-16") == content


@pytest.mark.asyncio
async def test_write_file(tmp_path):
    content = "foo\x00bar\x00baz\x00çäø☺"
    encoded_content_len = len(content.encode("utf-8"))

    alt_content = "boo\x00bar\x00baz\x00çäø☺"
    alt_content_len = "foo\x00bar"

    filename = tmp_path / "file"
    alt_filename = tmp_path / "file2"

    assert await write_file(filename, content, encoding="utf-8") is True
    assert filename.read_text(encoding="utf-8") == content

    assert await write_file(filename, content, encoding="utf-8") is True
    assert filename.read_text(encoding="utf-8") == content

    assert (
        await write_file(
            filename,
            content,
            encoding="utf-8",
            file_check_content=encoded_content_len - 1,
        )
        is True
    )
    assert filename.read_text(encoding="utf-8") == content

    assert (
        await write_file(
            filename, content, encoding="utf-8", file_check_content=encoded_content_len
        )
        is False
    )
    assert filename.read_text(encoding="utf-8") == content

    assert (
        await write_file(
            filename,
            content,
            encoding="utf-8",
            file_check_content=encoded_content_len + 1,
        )
        is False
    )
    assert filename.read_text(encoding="utf-8") == content

    assert (
        await write_file(
            filename,
            alt_content,
            encoding="utf-8",
            file_check_content=encoded_content_len,
        )
        is True
    )
    assert filename.read_text(encoding="utf-8") == alt_content

    assert (
        await write_file(
            alt_filename,
            alt_content,
            encoding="utf-8",
            file_check_content=encoded_content_len,
        )
        is True
    )
    assert alt_filename.read_text(encoding="utf-8") == alt_content

    assert (
        await write_file(
            alt_filename,
            alt_content_len,
            encoding="utf-8",
            file_check_content=encoded_content_len,
        )
        is True
    )
    assert alt_filename.read_text(encoding="utf-8") == alt_content_len
