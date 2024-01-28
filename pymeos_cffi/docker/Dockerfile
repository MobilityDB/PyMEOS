FROM pymeos/meos:latest
WORKDIR MobilityDB

RUN git fetch \
    && git checkout develop \
    && git pull


WORKDIR build

RUN cmake .. -DMEOS=on -DGEOS_INCLUDE_DIR=/usr/geos39/include/ -DGEOS_LIBRARY=/usr/geos39/lib64/libgeos_c.so -DGEOS_CONFIG=/usr/geos39/bin/geos-config -DPROJ_INCLUDE_DIRS=/usr/proj81/include/ -DPROJ_LIBRARIES=/usr/proj81/lib/libproj.so \
    && make -j \
    && make install

COPY build_wheels.sh /build_wheels.sh
RUN sed -i -e 's/\r$//' /build_wheels.sh \
    && chmod +x /build_wheels.sh \
    && rm -rf /opt/python/cp36-cp36m \
    && mkdir /wheelhouse_int

ENV LD_LIBRARY_PATH=/usr/lib64;/lib64

WORKDIR /

CMD ["/build_wheels.sh"]