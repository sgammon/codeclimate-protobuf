FROM sgammon/protoc-alpine:latest

MAINTAINER Sam Gammon <sam@bloombox.io>
LABEL maintainer "Sam Gammon <sam@bloombox.io>"

ADD engine.json /engine.json
ADD requirements.txt /requirements.txt
ADD dist/protolint-1.1.0.tar.gz /protolint

COPY .env/lib/python2.7/site-packages /protolint/site-packages
COPY protolint.sh /protolint.sh
RUN adduser -u 9000 -D -s /bin/false app \
    && cd /protolint/protolint-1.1.0 && python setup.py build install \
    && mkdir /.linter && chmod 777 /.linter

ENV PYTHONPATH "/protolint/protolint-1.1.0:/protolint/site-packages:/usr/lib/python2.7/site-packages"

WORKDIR /code
USER app
VOLUME /code
CMD ["bash", "/protolint.sh", "/config.json", "/code"]
