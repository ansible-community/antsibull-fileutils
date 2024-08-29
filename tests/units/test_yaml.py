# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

from __future__ import annotations

from io import BytesIO

import pytest

from antsibull_fileutils.yaml import (
    load_yaml_bytes,
    load_yaml_file,
    store_yaml_file,
    store_yaml_stream,
)

LOAD_YAML_DATA = [
    (
        """
foo: bar
""",
        {
            "foo": "bar",
        },
    ),
]


@pytest.mark.parametrize(
    "content, expected",
    LOAD_YAML_DATA,
)
def test_load_yaml(content, expected, tmp_path):
    assert load_yaml_bytes(content.encode("utf-8")) == expected

    file = tmp_path / "test.yaml"
    with file.open("w", encoding="utf-8") as f:
        f.write(content)
    assert load_yaml_file(file) == expected
    assert load_yaml_file(str(file)) == expected


STORE_YAML_DATA = [
    (
        {
            "foo": "bar",
        },
        """foo: bar
""",
    ),
]


@pytest.mark.parametrize(
    "content, expected",
    STORE_YAML_DATA,
)
def test_store_yaml(content, expected, tmp_path):
    file = tmp_path / "test.yaml"

    store_yaml_file(file, content)
    with file.open("r", encoding="utf-8") as f:
        assert f.read() == expected

    store_yaml_file(str(file), content)
    with file.open("r", encoding="utf-8") as f:
        assert f.read() == expected

    stream = BytesIO()
    store_yaml_stream(stream, content)
    assert stream.getvalue().decode("utf-8") == expected
