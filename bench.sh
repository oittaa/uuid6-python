#!/bin/bash
set -eu
TESTDIR=$(mktemp -d)
python -m pyperf timeit -o "${TESTDIR}/uuid1.json" -s "import uuid" "uuid.uuid1()"
python -m pyperf timeit -o "${TESTDIR}/uuid4.json" -s "import uuid" "uuid.uuid4()"
python -m pyperf timeit -o "${TESTDIR}/uuid6.json" -s "import uuid6" "uuid6.uuid6()"
python -m pyperf timeit -o "${TESTDIR}/uuid7.json" -s "import uuid6" "uuid6.uuid7()"
python -m pyperf compare_to --table "${TESTDIR}/uuid1.json" "${TESTDIR}/uuid4.json" "${TESTDIR}/uuid6.json" "${TESTDIR}/uuid7.json"
rm -rf -- "${TESTDIR}"
