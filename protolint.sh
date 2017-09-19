#!/bin/bash

PYTHONPATH="$(pwd):$PYTHONPATH" python -m protolint "$1" "$2"

