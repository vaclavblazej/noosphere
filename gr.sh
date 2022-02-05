#!/usr/bin/env bash

"$(dirname "$(realpath "${BASH_SOURCE[0]}")")"/run.py "$@" <&0 || exit
