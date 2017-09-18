
# protolint [![CircleCI](https://circleci.com/gh/sgammon/codeclimate-protobuf/tree/master.svg?style=svg)](https://circleci.com/gh/sgammon/codeclimate-protobuf/tree/master) [![Build Status](https://travis-ci.org/sgammon/codeclimate-protobuf.svg?branch=master)](https://travis-ci.org/sgammon/codeclimate-protobuf)  [![Code Climate](https://codeclimate.com/github/sgammon/codeclimate-protobuf/badges/gpa.svg)](https://codeclimate.com/github/sgammon/codeclimate-protobuf) [![Test Coverage](https://codeclimate.com/github/sgammon/codeclimate-protobuf/badges/coverage.svg)](https://codeclimate.com/github/sgammon/codeclimate-protobuf/coverage)
## support for `protobuf` in CodeClimate

- Latest Release: `v1.0.0`

This tool wraps `protoc-gen-lint` to generate improvement suggestions for your `.proto`s. It then outputs those items in CodeClimate's JSON format, so it can be used as a [CodeClimate Engine](http://blog.codeclimate.com/blog/2015/07/07/build-your-own-codeclimate-engine/).


### How it works

It's a Python module called `protolint`, with a module-level run file (`__main__.py`). It can be executed via any of the following methods:

Via the local bash script:
```bash
./protolint.sh <args...>
```

Via the virtualenv:
```bash
./activate && protolint <args...>
```

After installing globally, you can additionally execute it via:

Global module in Python:
```bash
python -m protolint <args...>
```

CLI tool:
```bash
protolint <args...>
```

The tool should output messages to `stderr` and JSON-formatted issues to `stdout`.
