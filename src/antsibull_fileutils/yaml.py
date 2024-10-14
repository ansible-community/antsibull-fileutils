# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021, Ansible Project

"""
YAML handling.
"""

from __future__ import annotations

import typing as t

import yaml

_SafeLoader: t.Any
_SafeDumper: t.Any
try:
    # use C version if possible for speedup
    from yaml import CSafeDumper as _SafeDumper
    from yaml import CSafeLoader as _SafeLoader
except ImportError:  # pragma: no cover
    from yaml import SafeDumper as _SafeDumper
    from yaml import SafeLoader as _SafeLoader

if t.TYPE_CHECKING:
    from _typeshed import StrOrBytesPath, SupportsWrite


class _IndentedDumper(yaml.SafeDumper):
    """
    Extend YAML dumper to increase indent of list items.
    """

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def load_yaml_bytes(data: bytes) -> t.Any:
    """
    Load and parse YAML from given bytes.
    """
    return yaml.load(data, Loader=_SafeLoader)


def load_yaml_file(path: StrOrBytesPath) -> t.Any:
    """
    Load and parse YAML file ``path``.
    """
    with open(path, "rb") as stream:
        return yaml.load(stream, Loader=_SafeLoader)


def store_yaml_file(
    path: StrOrBytesPath, content: t.Any, *, nice: bool = False, sort_keys: bool = True
) -> None:
    """
    Store ``content`` as YAML file under ``path``.
    """
    with open(path, "wb") as stream:
        store_yaml_stream(stream, content, nice=nice, sort_keys=sort_keys)


def store_yaml_stream(
    stream: SupportsWrite, content: t.Any, *, nice: bool = False, sort_keys: bool = True
) -> None:
    """
    Dump ``content`` as YAML to an IO ``stream``.
    """
    dumper = _IndentedDumper if nice else _SafeDumper
    dumper.ignore_aliases = lambda *args: True  # type: ignore[method-assign]
    yaml.dump(
        content,
        stream,
        default_flow_style=False,
        encoding="utf-8",
        Dumper=dumper,
        explicit_start=nice,
        sort_keys=sort_keys,
    )
