#!/bin/bash

PYTHONPATH="$(pwd):$PYTHONPATH" python -OO -m protolint "$1" "$2"
