FROM pymeos/meos:latest
WORKDIR MobilityDB

RUN git fetch
RUN git checkout master
RUN git pull


WORKDIR build

RUN cmake .. -DMEOS=on -DGEOS_INCLUDE_DIR=/usr/geos39/include/ -DGEOS_LIBRARY=/usr/geos39/lib64/libgeos_c.so -DGEOS_CONFIG=/usr/geos39/bin/geos-config
RUN make -j
RUN make install

COPY build_wheels.sh /build_wheels.sh
RUN sed -i -e 's/\r$//' /build_wheels.sh
RUN chmod +x /build_wheels.sh

RUN rm -rf /opt/python/cp36-cp36m
RUN rm -rf /opt/python/cp312-cp312
RUN mkdir /wheelhouse_int

ENV LD_LIBRARY_PATH=/usr/lib64;/lib64

WORKDIR /

CMD ["/build_wheels.sh"]