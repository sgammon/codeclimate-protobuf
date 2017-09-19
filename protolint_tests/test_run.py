# -*- coding: utf-8 -*-

"""

  testsuite: runner
  ~~~~~~~~~~~~~~~~~

"""

import unittest

import sys
import protolint
from .base import switchout_streams, restore_streams


class RunnerTests(unittest.TestCase):

  """ Test the entire `protolint` package. """

  def test_run_linter(self):

    """ test a full run of the linter """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample.json', 'protolint_tests/']
      run_tool()
    restore_streams()

  def test_run_linter_custom_config(self):

    """ test a full run of the linter with custom config """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_with_protopaths.json', 'protolint_tests/']
      run_tool()
    restore_streams()

  def test_run_linter_exclusion(self):

    """ test a full run of the linter with exclusions configured """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_with_exclusion.json', 'protolint_tests/']
      run_tool()
    restore_streams()

  def test_run_linter_empty(self):

    """ test a full run of the linter with an empty project """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_empty.json', 'protolint_tests/']
      run_tool()
    restore_streams()

  def test_run_linter_invalid_syntax_unexpected_token(self):

    """ test a full run of the linter with an unexpected token syntax error """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_invalid_syntax.json', 'protolint_tests/']
      run_tool()
    restore_streams()

  def test_run_linter_invalid_syntax_missing_close_bracket(self):

    """ test a full run of the linter with a missing close bracket """

    switchout_streams()
    with self.assertRaises(SystemExit) as exit:
      from protolint.__main__ import run_tool
      sys.argv = ['', 'protolint_tests/configs/sample_invalid_syntax2.json', 'protolint_tests/']
      run_tool()
    restore_streams()
