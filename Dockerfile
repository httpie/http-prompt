FROM python:alpine

ADD . /http-prompt/

RUN cd http-prompt && python setup.py install && cd ..

ENTRYPOINT ["http-prompt"]
