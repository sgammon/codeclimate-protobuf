
FROM python:2.7-alpine
MAINTAINER Sam Gammon <sam@bloombox.io>

RUN apk add --update \
      git \
      bash \
      make \
      curl \
      build-base \
      libtool \
      autoconf \
      automake \
      libstdc++ \
      qt5-qtbase \
      && curl --progress-bar https://codeload.github.com/google/protobuf/tar.gz/v3.4.1 > protobuf.tar.gz \
      && tar -xzvf protobuf.tar.gz \
      && cd protobuf-3.4.1 && ./autogen.sh && ./configure --prefix /usr && make && make install \
      && apk del \
        build-base \
        curl \
        git \
        libtool \
        make \
        autoconf \
        automake \
      && rm -rfv /usr/share/autoconf /usr/share/automake-1.15 /usr/share/perl5 /usr/lib/perl5 /var/cache/apk/* protobuf /usr/local/go/pkg /usr/lib/go/pkg/tool /protobuf-3.4.1 /protobuf.tar.gz

COPY ./protoc-gen-lint /bin/protoc-gen-lint
