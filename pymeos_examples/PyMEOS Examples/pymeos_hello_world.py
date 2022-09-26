from pymeos import TGeomPointInst, TGeomPointSeqSet, TGeomPointSeq
from pymeos_cffi import meos_initialize, meos_finish


def main():
    # Initialize session_timezone
    meos_initialize()

    # Input temporal points in WKT format
    inst_wkt = "POINT(1 1)@2000-01-01"
    iset_wkt = "{POINT(1 1)@2000-01-01, POINT(2 2)@2000-01-02}"
    seq_wkt = "[POINT(1 1)@2000-01-01, POINT(2 2)@2000-01-02]"
    ss_wkt = "{[POINT(1 1)@2000-01-01, POINT(2 2)@2000-01-02],[POINT(3 3)@2000-01-03, POINT(3 3)@2000-01-04]}"

    # Read WKT into temporal point object
    inst = TGeomPointInst(string=inst_wkt)
    iset = TGeomPointSeq(string=iset_wkt)
    seq = TGeomPointSeq(string=seq_wkt)
    ss = TGeomPointSeqSet(string=ss_wkt)

    results = [
        ('Temporal Instant', inst_wkt, inst.as_mf_json()),
        ('Temporal Instant Set (Sequence with discrete interpolation)', iset_wkt, iset.as_mf_json()),
        ('Temporal Sequence', seq_wkt, seq.as_mf_json()),
        ('Temporal Sequence Set', ss_wkt, ss.as_mf_json()),
    ]

    for description, wkt, mfjson in results:
        print("\n"
              "--------------------\n"
              f"| {description} |\n"
              "--------------------\n\n"
              "WKT:\n"
              f"----\n{wkt}\n\n"
              "MF-JSON:\n"
              f"--------\n{mfjson}\n")

    # Finalize MEOS
    meos_finish()


if __name__ == '__main__':
    main()
