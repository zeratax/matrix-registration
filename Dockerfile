FROM alpine:latest

COPY . /tmp/

RUN apk --update add --no-cache python3 postgresql-libs && \
    apk add --no-cache --virtual .build-deps python3-dev gcc musl-dev postgresql-dev && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip && \
    pip install waitress && pip install /tmp && \
    rm -rf /tmp/* && \
    apk --purge del .build-deps


VOLUME ["/data"]

EXPOSE 5000/tcp

ENTRYPOINT ["/usr/bin/python", "/usr/bin/matrix_registration", "--config-path=/data/config.yaml"]

