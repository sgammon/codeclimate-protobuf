FROM sgammon/protoc-alpine:latest

MAINTAINER Sam Gammon <sam@bloombox.io>

RUN adduser -u 9000 -D -s /bin/false app
ADD engine.json /engine.json
ADD requirements.txt /requirements.txt
ADD dist/protolint-1.0.2.tar.gz /protolint
COPY .env/lib/python2.7/site-packages /protolint/site-packages
COPY protolint.sh /protolint.sh
RUN cd /protolint/protolint-1.0.2 && python setup.py build install && mkdir /.linter && chmod 777 /.linter
ENV PYTHONPATH "/protolint/protolint-1.0.2:/protolint/site-packages:/usr/lib/python2.7/site-packages"
WORKDIR /code
USER app
VOLUME /code
CMD ["bash", "/protolint.sh"]
