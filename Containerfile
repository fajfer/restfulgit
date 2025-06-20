FROM docker.io/python:3-alpine3.22

ENV PYTHONBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1

RUN mkdir -p /app/run /app/src/restfulgit && \
    adduser --no-create-home --gecos "restfulgit daemon" --disabled-password \
    --home /app/run --uid 35004 restfulgit

ARG LIBGIT2_VER=1.9.1
WORKDIR /app/src/restfulgit

RUN apk upgrade && \
    apk add --no-cache \
    git python3-dev gcc binutils musl-dev py3-pip \
    libffi-dev make cmake krb5-dev openssl-dev libssh2-dev

RUN cd /app/src && \
    wget -qO - https://github.com/libgit2/libgit2/archive/v${LIBGIT2_VER}.tar.gz | \
    tar xzf - && \
    cd libgit2-${LIBGIT2_VER} && \
    mkdir build && cd build && \
    cmake -DCMAKE_INSTALL_LIBDIR=lib .. && \
    cmake --build . && \
    cmake --install . --prefix /usr/local && \
    cd /app/src && \
    rm -rf libgit2-${LIBGIT2_VER}

RUN python3 -m venv /app/env 
RUN /app/env/bin/pip install -U pip wheel
ENV VIRTUAL_ENV=/app/env \
    PATH=/app/env/bin:$PATH

COPY requirements.txt /app/src/restfulgit
RUN /app/env/bin/pip install -Ur requirements.txt
COPY . /app/src/restfulgit
RUN /app/env/bin/pip install .

# RUN /app/env/bin/pip install pycodestyle pylint Flask-Testing coverage nose coveralls filemagic
# RUN git branch ambiguous 1f51b91ac383806df9d322ae67bbad3364f50811 && \
#     git checkout -b master ; \
#     umask 0022

USER 35004:35004
EXPOSE 8080/tcp
CMD ["/app/env/bin/restfulgit"]
