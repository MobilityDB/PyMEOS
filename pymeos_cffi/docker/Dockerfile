FROM quay.io/pypa/manylinux2014_x86_64

RUN yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
RUN yum -y update
RUN yum -y install gcc gcc-c++ make cmake postgresql13-devel proj-devel json-c-devel geos-devel
RUN git clone --branch develop https://github.com/MobilityDB/MobilityDB
WORKDIR MobilityDB/build
RUN cmake .. -DMEOS=on -DDOC_DEV=on
RUN make -j
RUN make install

RUN cp /MobilityDB/postgis/postgis_revision.h /usr/local/include/
RUN cp /MobilityDB/postgis/postgis_config.h /usr/local/include/
RUN cp /MobilityDB/postgis/liblwgeom/lwinline.h /usr/local/include/

COPY postgres.h /usr/local/include/postgres.h
COPY liblwgeom.h /usr/local/include/liblwgeom.h

COPY meos_mod.h /usr/local/include/meos_mod.h

COPY build_wheels.sh /build_wheels.sh
RUN chmod +x /build_wheels.sh

RUN rm -rf /opt/python/cp36-cp36m
RUN mkdir /wheelhouse_int

ENV LD_LIBRARY_PATH=/usr/lib64;/lib64

WORKDIR /

CMD ["./build_wheels.sh"]