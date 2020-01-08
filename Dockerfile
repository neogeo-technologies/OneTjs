FROM python:3.6.4

MAINTAINER Benjamin Chartier at neogeo.fr

RUN mkdir /onetjs
RUN mkdir /onetjs/log
COPY requirements.txt /onetjs/
RUN pip install -r /onetjs/requirements.txt

COPY app /onetjs/app
COPY data /onetjs/data
COPY static /onetjs/static
COPY *.cfg /onetjs/
COPY uwsgi.ini /onetjs/

WORKDIR /onetjs
VOLUME /onetjs/data
VOLUME /onetjs/log
ENV ONETJS_CONFIG_FILE_PATH /onetjs/docker.cfg

CMD ["uwsgi", "--socket", "0.0.0.0:8000", \
               "--protocol", "http", \
               "--ini", "uwsgi.ini"]