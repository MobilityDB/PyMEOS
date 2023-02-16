## 1.2.0

### Breaking changes

- All `@property` decorators have been removed to reflect that the elements return are computed.
  They may be added again in the future, probably with some caching mechanism.
- `Period` method `distance` now returns a `datetime.timedelta` with the distance instead
  of returning the number of seconds.
- `BaseGranularityAggregator` renamed to `BaseGranularAggregator`

## 1.1.2

- Add support for `asyncpg`.
- Add support for `psycopg` (psycopg v3).

### Breaking changes

- `MobilityDB` using `psycopg2` has been moved from `pymeos.db` to `pymeos.db.psycopg2` due to the addition of `asyncpg` 
   and `psycopg` support.

## 1.1.1

- All MEOS functions added to PyMEOS.

## 1.1.0

### Breaking changes

- Function `meos_initialize` is now called `pymeos_initialize` and can receive a `str` parameter stating the desired
  timezone (e.b. `pymeos_initialize('UTC')`)
- Function `meos_finish` is now called `pymeos_finalize`.

## 1.0.0

Use MEOS as backend.