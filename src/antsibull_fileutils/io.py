# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021, Ansible Project
"""I/O helper functions."""

from __future__ import annotations

import os
import os.path
import typing as t

import aiofiles

if t.TYPE_CHECKING:
    from _typeshed import StrOrBytesPath


async def copy_file(
    source_path: StrOrBytesPath,
    dest_path: StrOrBytesPath,
    *,
    check_content: bool = True,
    file_check_content: int = 0,
    chunksize: int,
) -> bool:
    """
    Copy content from one file to another.

    :arg source_path: Source path. Must be a file.
    :arg dest_path: Destination path.
    :kwarg check_content: If ``True`` (default) and ``file_check_content > 0`` and the
        destination file exists, first check whether source and destination are potentially equal
        before actually copying,
    :return: ``True`` if the file was actually copied.
    """
    if check_content and file_check_content > 0:
        # Check whether the destination file exists and has the same content as the source file,
        # in which case we won't overwrite the destination file
        try:
            stat_d = os.stat(dest_path)
            if stat_d.st_size <= file_check_content:
                stat_s = os.stat(source_path)
                if stat_d.st_size == stat_s.st_size:
                    # Read both files and compare
                    async with aiofiles.open(source_path, "rb") as f_in:
                        content_to_copy = await f_in.read()
                    async with aiofiles.open(dest_path, "rb") as f_in:
                        existing_content = await f_in.read()
                    if content_to_copy == existing_content:
                        return False
                    # Since we already read the contents of the file to copy, simply write it to
                    # the destination instead of reading it again
                    async with aiofiles.open(dest_path, "wb") as f_out:
                        await f_out.write(content_to_copy)
                    return True
        except FileNotFoundError:
            # Destination (or source) file does not exist
            pass

    async with aiofiles.open(source_path, "rb") as f_in:
        async with aiofiles.open(dest_path, "wb") as f_out:
            while chunk := await f_in.read(chunksize):
                await f_out.write(chunk)
    return True


async def write_file(
    filename: StrOrBytesPath,
    content: str,
    *,
    file_check_content: int = 0,
    encoding: str = "utf-8",
) -> bool:
    """
    Write encoded content to file.

    :arg filename: The filename to write to.
    :arg content: The content to write to the file.
    :kwarg file_check_content: If > 0 and the file exists and its size in bytes does not exceed this
        value, will read the file and compare it to the encoded content before overwriting.
    :return: ``True`` if the file was actually written.
    """

    content_bytes = content.encode(encoding)

    if file_check_content > 0 and len(content_bytes) <= file_check_content:
        # Check whether the destination file exists and has the same content as the one we want to
        # write, in which case we won't overwrite the file
        try:
            stat = os.stat(filename)
            if stat.st_size == len(content_bytes):
                # Read file and compare
                async with aiofiles.open(filename, "rb") as f:
                    existing_content = await f.read()
                if existing_content == content_bytes:
                    return False
        except FileNotFoundError:
            # Destination file does not exist
            pass

    async with aiofiles.open(filename, "wb") as f:
        await f.write(content_bytes)
    return True


async def read_file(filename: StrOrBytesPath, *, encoding: str = "utf-8") -> str:
    """
    Read the file and decode its contents with the given encoding.

    :arg filename: The filename to read from.
    :kwarg encoding: The encoding to use.
    """
    async with aiofiles.open(filename, "r", encoding=encoding) as f:
        content = await f.read()

    return content
