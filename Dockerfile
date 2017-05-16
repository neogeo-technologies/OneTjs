FROM python:2.7

MAINTAINER Benjamin Chartier at neogeo.fr

# TODO: declare volume for logs
RUN mkdir /tjs
RUN mkdir /tjs/log
COPY requirements.txt /tjs/
COPY manage.py /tjs/
COPY app /tjs/app
COPY data /tjs/data
COPY static /tjs/static
COPY *.cfg /tjs/
RUN pip install -r /tjs/requirements.txt

WORKDIR /tjs
ENTRYPOINT ["python"]
CMD ["manage.py", "-c", "docker.cfg", "runserver", "-h",  "0.0.0.0", "-p", "5000"]
