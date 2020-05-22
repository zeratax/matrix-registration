FROM alpine:latest

RUN apk --update add python3 && \
    rm -rf /var/lib/apt/lists/* && \
    rm /var/cache/apk/* && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip

COPY . /tmp/

RUN pip install waitress && pip install /tmp && rm -rf /tmp/*

VOLUME ["/data"]

EXPOSE 5000/tcp

ENTRYPOINT ["/usr/bin/python", "/usr/bin/matrix_registration", "--config-path=/data/config.yaml"]

