#!/usr/bin/env sh
# vim:set sw=4 ts=8 fileencoding=utf8:
# SPDX-License-Identifier: BSD-2-Clause
# SPDX-FileCopyrightText: 2025 Сергей Леонтьев (leo@sai.msu.ru)

set -e
uv run --group dev ruff check .
uv run --group dev ruff format --check .
