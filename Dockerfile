FROM sgammon/protoc-alpine:latest

MAINTAINER Sam Gammon <sam@bloombox.io>

RUN adduser -u 9000 -D -s /bin/false app
ADD engine.json /engine.json
ADD dist/protolint-1.0.1.tar.gz /protolint
COPY protolint_tests /protolint_tests
RUN cd /protolint/protolint-1.0.1 && python setup.py build install && mkdir /.linter && chmod 777 /.linter
ENV PYTHONPATH "/protolint/protolint-1.0.1:$PYTHONPATH"
WORKDIR /code
USER app
VOLUME /code
CMD ["python", "-OO", "-m protolint"]
