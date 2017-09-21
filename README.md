
# protolint [![CircleCI](https://circleci.com/gh/sgammon/codeclimate-protobuf/tree/master.svg?style=svg)](https://circleci.com/gh/sgammon/codeclimate-protobuf/tree/master) [![Build Status](https://travis-ci.org/sgammon/codeclimate-protobuf.svg?branch=master)](https://travis-ci.org/sgammon/codeclimate-protobuf)  [![Code Climate](https://codeclimate.com/github/sgammon/codeclimate-protobuf/badges/gpa.svg)](https://codeclimate.com/github/sgammon/codeclimate-protobuf) [![Test Coverage](https://codeclimate.com/github/sgammon/codeclimate-protobuf/badges/coverage.svg)](https://codeclimate.com/github/sgammon/codeclimate-protobuf/coverage) [![Issue Count](https://codeclimate.com/github/sgammon/codeclimate-protobuf/badges/issue_count.svg)](https://codeclimate.com/github/sgammon/codeclimate-protobuf)
## support for `protobuf` in CodeClimate

- Latest Release: `v1.1.4`
- `protoc` Version: `v3.4.1`

This tool wraps `protoc-gen-lint` to generate improvement suggestions for your `.proto`s. It then outputs those items in CodeClimate's JSON format, so it can be used as a [CodeClimate Engine](http://blog.codeclimate.com/blog/2015/07/07/build-your-own-codeclimate-engine/).


### Configuration

There is a custom configuration entry - `protopaths` - that lets you specify `-I`/`--protos_path=` flags to the `protoc` compiler. If your `.proto` files use `import "...";` directives, you probably need this. Here's how you do it:

```yaml
engines:
  protolint:
    enabled: true
    config:
      protopaths:
        - sources/models/pathone
        - sources/models/pathtwo
```


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
