# -*- coding: utf-8 -*-

"""

  protolint: entrypoint
  ~~~~~~~~~~~~~~~~~~~~~

"""

import sys
import pprint

from . import cli
from . import config
from . import linter
from . import output


# declare globals
linter_config = None


def run_tool():

  """ Run the CLI tool. """

  global linter_config

  args = cli.parser.parse_args()

  if not args.config:
    output.error("Must provide argument 'config'. See --help for more.")
  if not args.workspace:
    output.error("Must provide argument 'workspace'. See --help for more.")

  filepath, workspace = (args.config, args.workspace)

  output.info('Preparing to scan workspace "%s"...' % workspace)
  linter_config = config.LinterConfig(filepath, workspace)

  protolint = linter.Linter(linter_config, args)

  for issue in protolint():
    issue.write()

  output.info('All done.')
  sys.exit(0)

if __name__ == "__main__": run_tool()
