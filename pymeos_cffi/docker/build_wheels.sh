#!/bin/bash
set -e -u
#
# Command: docker run --rm -ti -v <path-to-pymeos-project>:/PyMEOS -v <path-to-store-wheels>:/wheelhouse pymeos/builder
# Example: docker run --rm -ti -v /home/diviloper/MobilityDB/PyMEOS:/PyMEOS -v /home/diviloper/MobilityDB/PyMEOS/pymeos_cffi/dist:/wheelhouse pymeos/builder
#
function repair_wheel {
  wheel="$1"
  if ! auditwheel -v show "$wheel"; then
    echo "Skipping non-platform wheel $wheel"
  else
    auditwheel -v repair "$wheel" -w /wheelhouse/
  fi
}

for PYBIN in /opt/python/cp*/bin; do
  echo "================START $PYBIN================"
  echo "================COMPILE================"
  "${PYBIN}/pip" install -r /PyMEOS/pymeos_cffi/dev-requirements.txt
  "${PYBIN}/pip" wheel /PyMEOS/pymeos_cffi/ --no-deps -w /wheelhouse_int/

  echo "==============REPAIR=============="
  for whl in wheelhouse_int/*.whl; do
    repair_wheel "$whl"
    rm "$whl"
  done
  echo "==============TEST=============="
  "${PYBIN}/pip" install pymeos_cffi --pre -f /wheelhouse
  "${PYBIN}/python" -c "from pymeos_cffi import meos_initialize, meos_finalize; meos_initialize('UTC'); meos_finalize()"
  echo "==============FINISH $PYBIN========="
done