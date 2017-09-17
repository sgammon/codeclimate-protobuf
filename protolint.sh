#!/bin/bash

PYTHONPATH="`pwd`:$PYTHONPATH" .env/bin/python -OO -m protolint $1 $2
