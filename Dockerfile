FROM python:3.10.6

WORKDIR /www

# install all files
COPY ./ /www

# set config and create files directories
RUN cp /www/config.server.py /www/config.py

RUN apt-get update && \
    apt-get install -y git gcc make libssl-dev cmake && \
    git clone https://github.com/MariaDB/mariadb-connector-c.git && \
    mkdir build && cd build && \
    cmake ../mariadb-connector-c/ -DCMAKE_INSTALL_PREFIX=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ./mariadb-connector-c && rm -rf build

RUN pip3 install -r /www/install/requirements.txt

CMD [ "python", "-u", "/www/api.py" ]