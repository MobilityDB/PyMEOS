FROM quay.io/pypa/manylinux2014_x86_64

RUN yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
RUN yum -y update
RUN yum -y install gcc gcc-c++ make cmake postgresql13-devel proj-devel json-c-devel geos39-devel gsl-devel
RUN git clone https://github.com/MobilityDB/MobilityDB
