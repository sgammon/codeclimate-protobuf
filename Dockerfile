FROM sgammon/protoc-alpine:latest

MAINTAINER Sam Gammon <sam@bloombox.io>

RUN adduser -u 9000 -D -s /bin/false app
ADD dist/protolint-1.0.0.tar.gz /protolint
COPY protolint_tests /protolint_tests
RUN apk update && apk add protobuf python git && go get github.com/ckaznocha/protoc-gen-lint
RUN cd /protolint/protolint-1.0.0 && python setup.py build install && mkdir /.linter && chmod 777 /.linter
ENV PYTHONPATH "/protolint/protolint-1.0.0:$PYTHONPATH"
WORKDIR /code
USER app
VOLUME /code
CMD ["python", "-OO", "-m protolint"]
