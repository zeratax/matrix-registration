ARG PYTHON_VERSION=3.8
ARG ALPINE_VERSION=3.12

# builder

FROM docker.io/python:${PYTHON_VERSION}-alpine${ALPINE_VERSION} as builder


RUN apk add \
        build-base \
		musl-dev \
		postgresql-dev

COPY README.md setup.py config.sample.yaml /tmp/matrix-registration/
COPY matrix_registration /tmp/matrix-registration/matrix_registration/

RUN pip install --prefix="/install" --no-warn-script-location \
		/tmp/matrix-registration[postgres]

# Runtime
FROM docker.io/python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}

RUN apk add --no-cache --virtual .runtime_deps \
		postgresql-libs

COPY --from=builder /install /usr/local

VOLUME ["/data"]

EXPOSE 5000/tcp

ENTRYPOINT ["matrix-registration", "--config-path=/data/config.yaml"]
