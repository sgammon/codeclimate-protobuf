#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='protolint',
      version='1.0.0',
      description='CodeClimate linter for Protobuf, using protoc-gen-lint',
      author='Sam Gammon',
      author_email='sam@bloombox.io',
      url='https://github.com/sgammon/codeclimate-protolint',
      packages=['protolint', 'protolint_tests'])
