# -*- coding: utf-8 -*-

"""

  testsuite: CLI
  ~~~~~~~~~~~~~~

"""

import unittest

import protolint
from .base import switchout_streams, restore_streams


class CLITests(unittest.TestCase):

  """ Test the `protolint.cli` package. """

  def test_parser(self):

    """ load the parser and make sure it's there """

    from protolint import cli
    assert cli.parser, "parser must exist"

  def test_parser_empty(self):

    """ test that the parser can print empty args """

    from protolint import cli
    switchout_streams()
    with self.assertRaises(SystemExit):
      arguments = cli.parser.parse_args([])
    restore_streams()

  def test_parser_missing(self):

    """ test that the parser can parse missing args and fail """

    switchout_streams()
    with self.assertRaises(SystemExit):
      from protolint import cli
      arguments = cli.parser.parse_args(['one_arg'])
    restore_streams()

  def test_parser_version(self):

    """ test that the parser can produce the version """

    switchout_streams()
    with self.assertRaises(SystemExit):
      from protolint import cli
      arguments = cli.parser.parse_args(['--version'])
   
    stdout, stderr = restore_streams()
    value = stderr.getvalue()

    self.assertTrue('protolint' in value, "version output must contain name of app. got: '%s'" % stdout.getvalue())
    self.assertTrue(('.'.join(map(unicode, protolint.__version__))) in value, "version output must contain version. got: '%s'" % stdout.getvalue())

  def test_parser_help(self):

    """ test that the parser can produce help output """

    switchout_streams()
    with self.assertRaises(SystemExit):
      from protolint import cli
      arguments = cli.parser.parse_args(['--help'])

    stdout, stderr = restore_streams()
    value = stdout.getvalue()

    self.assertTrue('usage' in value, "help output must contain usage info. got: '%s'" % value)

  def test_parser_valid(self):

    """ test that the parser can parse missing args and fail """

    switchout_streams()
    from protolint import cli
    arguments = cli.parser.parse_args(['protolint_tests/configs/sample.json', 'protolint_tests/'])
    self.assertTrue(arguments.config, "config file must properly get parsed")
    self.assertTrue(arguments.workspace, "workspace location must properly get parsed")
    restore_streams()
