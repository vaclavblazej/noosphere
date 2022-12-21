#!/usr/bin/env bash

"$(dirname "$(realpath "${BASH_SOURCE[0]}")")"/bin/run.py "$@" <&0 || exit
