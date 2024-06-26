FROM python:3.8
RUN apt-get update && \
    apt-get install -y patchelf
RUN python -m pip install Cython pytest coverage pytest-cov

WORKDIR /tmp/compile
ADD . /tmp/compile/

ENV DEBUG=1

RUN python setup.py install && \
    chmod ugo+x /tmp/compile/tests/test.sh

CMD ["/tmp/compile/tests/test.sh"]
