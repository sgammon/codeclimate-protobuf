# -*- coding: utf-8 -*-

"""

  protolint: CLI
  ~~~~~~~~~~~~~~

"""

import argparse
from . import __version__ as version


parser = argparse.ArgumentParser(
  prog='protolint',
  description='Lint Protobuf models, enums and services.')


## -- Required Params

# Add `config_file_path` parameter
parser.add_argument('config',
                    type=unicode,
                    help='path to the config file for codeclimate linting')

# Add `workspace_path` parameter
parser.add_argument('workspace',
                    type=unicode,
                    help='path to the workspace presumably full of protos')


## -- Optional Params

# `--version` to report version
parser.add_argument('--version', '-v',
                    action='version',
                    version='%(prog)s ' + '.'.join(map(unicode, version)))
