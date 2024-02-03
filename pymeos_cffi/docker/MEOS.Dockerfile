FROM quay.io/pypa/manylinux2014_x86_64

RUN yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm \
    && yum -y update \
    && yum -y install gcc gcc-c++ make cmake postgresql13-devel proj81-devel json-c-devel geos39-devel gsl-devel \
    && git clone https://github.com/MobilityDB/MobilityDB
