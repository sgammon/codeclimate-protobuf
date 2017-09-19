# -*- coding: utf-8 -*-

"""

  protolint: output
  ~~~~~~~~~~~~~~~~~

"""

# pragma: no cover

import sys
import json
import logging
import colorlog


colorlog.basicConfig(
  stream=sys.stderr,
  level=logging.DEBUG,
  format="[%(log_color)s%(levelname)s%(reset)s] %(name)s: %(message)s")


logger = colorlog.getLogger('protolint')


def say(*arguments):

  """ Say something verbosely to the log. """

  if __debug__:  # pragma: no cover
    logger.debug(" ".join(map(unicode, arguments)))


def info(*arguments):

  """ Say something verbosely to the log. """

  if __debug__:  # pragma: no cover
    logger.info(" ".join(map(unicode, arguments)))


def warn(*arguments):

  """ Issue a warning to the log. """

  if __debug__:  # pragma: no cover
    logger.warning(" ".join(map(unicode, arguments)))


def error(*arguments):

  """ Output an error to the log. """

  if __debug__:  # pragma: no cover
    logger.error(" ".join(map(unicode, arguments)))


def critical(*arguments):

  """ Output a critical message to the log. """

  if __debug__:  # pragma: no cover
    logger.critical(" ".join(map(unicode, arguments)))


def issue(detected):  # pragma: no cover

  """ Output a CodeClimate-formatted JSON issue to `stdout`.

    :param detected: Detected `linter.Issue` object to format. """

  value = detected()
  if value:
    print >> sys.stdout, value
