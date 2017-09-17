# -*- coding: utf-8 -*-

"""

  testsuite: base
  ~~~~~~~~~~~~~~~

"""

import sys
import unittest

try:
  import cStringIO as StringIO
except ImportError:
  import StringIO


# Globals
stdout_stream = None
stderr_stream = None


def switchout_streams():

  """ Stub stdout and stderr for testing. """

  global stdout_stream
  global stderr_stream

  stdout_stream = sys.stdout
  stderr_stream = sys.stderr
  sys.stdout = StringIO.StringIO()
  sys.stderr = StringIO.StringIO()


def restore_streams():

  """ Restore the stdout and stderr streams. """

  global stdout_stream
  global stderr_stream

  streams = (sys.stdout, sys.stderr)

  sys.stdout = stdout_stream
  sys.stderr = stderr_stream
  stdout_stream = None
  stderr_stream = None

  return streams
