## 1.2.0

- Add support for `asyncpg`.

### Breaking changes

- `MobilityDB` using `psycopg2` has been moved from `pymeos.db` to `pymeos.db.psycopg` due to the addition of `asyncpg` support.

## 1.1.1

All MEOS functions are added to PyMEOS.

## 1.1.0

### Breaking changes

- Function `meos_initialize` is now called `pymeos_initialize` and can receive a `str` parameter stating the desired
  timezone (e.b. `pymeos_initialize('UTC')`)
- Function `meos_finish` is now called `pymeos_finalize`.

## 1.0.0

Use MEOS as backend.