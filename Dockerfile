FROM python:3.9

WORKDIR /www

# install all files
COPY ./ /www

# set config and create files directories
RUN cp /www/config.server.py /www/config.py

# Install connector
RUN apt-get install -y apt-transport-https
RUN apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db
RUN curl -LsS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash
RUN apt-get update
RUN apt-get upgrade -y 
RUN apt-get dist-upgrade
RUN apt-get install libmariadb3 libmariadb-dev
RUN pip3 install -r /www/install/requirements.txt

CMD [ "python", "-u", "/www/api.py" ]