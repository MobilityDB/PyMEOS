FROM debian:buster-slim

RUN apt install build-essential cmake postgresql-server-dev-11 liblwgeom-dev libproj-dev libjson-c-dev libprotobuf-c-dev

RUN git clone --branch develop https://github.com/MobilityDB/MobilityDB
WORKDIR MobilityDB/build




