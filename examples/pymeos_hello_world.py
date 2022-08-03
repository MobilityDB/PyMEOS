import _meos_cffi

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib


def main():
    # Initialize session_timezone
    _lib.meos_initialize()

    # Input temporal points in WKT format
    inst_wkt = "POINT(1 1)@2000-01-01"
    iset_wkt = "{POINT(1 1)@2000-01-01, POINT(2 2)@2000-01-02}"
    seq_wkt = "[POINT(1 1)@2000-01-01, POINT(2 2)@2000-01-02]"
    ss_wkt = "{[POINT(1 1)@2000-01-01, POINT(2 2)@2000-01-02],[POINT(3 3)@2000-01-03, POINT(3 3)@2000-01-04]}"

    # Read WKT into temporal point object
    inst = _lib.tgeompoint_in(inst_wkt.encode('utf-8'))
    iset = _lib.tgeompoint_in(iset_wkt.encode('utf-8'))
    seq = _lib.tgeompoint_in(seq_wkt.encode('utf-8'))
    ss = _lib.tgeompoint_in(ss_wkt.encode('utf-8'))

    # Convert result to MF-JSON
    inst_mfson = _lib.temporal_as_mfjson(inst, True, 3, 6, _ffi.NULL)
    inst_mfson = _ffi.string(inst_mfson).decode('utf-8')
    print("\n"
          "--------------------\n"
          "| Temporal Instant |\n"
          "--------------------\n\n"
          "WKT:\n"
          f"----\n{inst_wkt}\n\n"
          "MF-JSON:\n"
          f"--------\n{inst_mfson}\n")

    iset_mfson = _lib.temporal_as_mfjson(iset, True, 3, 6, _ffi.NULL)
    iset_mfson = _ffi.string(iset_mfson).decode('utf-8')
    print("\n"
          "------------------------\n"
          "| Temporal Instant Set |\n"
          "------------------------\n\n"
          "WKT:\n"
          f"----\n{iset_wkt}\n\n"
          "MF-JSON:\n"
          f"--------\n{iset_mfson}\n")
    seq_mfson = _lib.temporal_as_mfjson(seq, True, 3, 6, _ffi.NULL)
    seq_mfson = _ffi.string(seq_mfson).decode('utf-8')
    print("\n"
          "---------------------\n"
          "| Temporal Sequence |\n"
          "---------------------\n\n"
          "WKT:\n"
          f"----\n{seq_wkt}\n\n"
          "MF-JSON:\n"
          f"--------\n{seq_mfson}\n")
    ss_mfson = _lib.temporal_as_mfjson(ss, True, 3, 6, _ffi.NULL)
    ss_mfson = _ffi.string(ss_mfson).decode('utf-8')
    print("\n"
          "-------------------------\n"
          "| Temporal Sequence Set |\n"
          "-------------------------\n\n"
          "WKT:\n"
          f"----\n{ss_wkt}\n\n"
          "MF-JSON:\n"
          f"--------\n{ss_mfson}\n")

    # Finalize MEOS
    _lib.meos_finish()


if __name__ == '__main__':
    main()
