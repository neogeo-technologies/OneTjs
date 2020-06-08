FROM python:3.6

MAINTAINER Benjamin Chartier at neogeo.fr

RUN mkdir /onetjs
RUN mkdir /onetjs/log
COPY requirements.txt /onetjs/
RUN pip install -r /onetjs/requirements.txt

COPY onetjs /onetjs/onetjs
COPY data /onetjs/data
COPY static /onetjs/static
COPY setup.py *.cfg /onetjs/
COPY uwsgi.ini /onetjs/

WORKDIR /onetjs
VOLUME /onetjs/data
VOLUME /onetjs/log
ENV ONETJS_CONFIG_FILE_PATH /onetjs/docker.cfg

RUN apt update; apt install -y apache2 apache2-dev

RUN a2dismod mpm_event
RUN a2enmod mpm_prefork
RUN pip install mod-wsgi

RUN mod_wsgi-express module-config > /etc/apache2/mods-enabled/wsgi.load
COPY apache_onetjs.conf /etc/apache2/sites-enabled/000-default.conf  
RUN sed -i 's/ErrorLog.*/ErrorLog \/dev\/sdtout/' /etc/apache2/apache2.conf
RUN pip install -e .
CMD ["apache2ctl", "-D", "FOREGROUND"]
