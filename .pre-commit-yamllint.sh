#!/usr/bin/env sh
# vim:set sw=4 ts=8 fileencoding=utf8:
# SPDX-License-Identifier: BSD-2-Clause
# SPDX-FileCopyrightText: 2025 Сергей Леонтьев (leo@sai.msu.ru)

for f in "$@" ; do
    case "${f}" in
     *.yml|*.yaml)
	 printf "${f}\0"
	 ;;
    esac
done | xargs -0 yamllint
