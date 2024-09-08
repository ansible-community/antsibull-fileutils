# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024, Ansible Project

"""
Utilities
"""

from __future__ import annotations


def collect_log(with_debug: bool = True, with_info: bool = True):
    debug = []
    info = []

    def log_debug(msg: str, *args) -> None:
        debug.append((msg, args))

    def log_info(msg: str, *args) -> None:
        info.append((msg, args))

    kwargs = {}
    if with_debug:
        kwargs["log_debug"] = log_debug
    if with_info:
        kwargs["log_info"] = log_info
    return (
        kwargs,
        debug,
        info,
    )
