#!/usr/bin/env bash

"$(dirname "$(realpath "${BASH_SOURCE[0]}")")"/src/noosphere/run.py "$@" <&0 || exit
