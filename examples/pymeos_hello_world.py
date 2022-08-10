from pymeos import TGeomPointInst, TGeomPointInstSet, TGeomPointSeqSet, TGeomPointSeq
from pymeos_cffi.functions import meos_initialize, meos_finish


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
    iset = TGeomPointInstSet(string=iset_wkt)
    seq = TGeomPointSeq(string=seq_wkt)
    ss = TGeomPointSeqSet(string=ss_wkt)

    # Convert result to MF-JSON
    inst_mfson = inst.as_mf_json()
    print("\n"
          "--------------------\n"
          "| Temporal Instant |\n"
          "--------------------\n\n"
          "WKT:\n"
          f"----\n{inst_wkt}\n\n"
          "MF-JSON:\n"
          f"--------\n{inst_mfson}\n")

    iset_mfson = iset.as_mf_json()
    print("\n"
          "------------------------\n"
          "| Temporal Instant Set |\n"
          "------------------------\n\n"
          "WKT:\n"
          f"----\n{iset_wkt}\n\n"
          "MF-JSON:\n"
          f"--------\n{iset_mfson}\n")
    seq_mfson = seq.as_mf_json()
    print("\n"
          "---------------------\n"
          "| Temporal Sequence |\n"
          "---------------------\n\n"
          "WKT:\n"
          f"----\n{seq_wkt}\n\n"
          "MF-JSON:\n"
          f"--------\n{seq_mfson}\n")
    ss_mfson = ss.as_mf_json()
    print("\n"
          "-------------------------\n"
          "| Temporal Sequence Set |\n"
          "-------------------------\n\n"
          "WKT:\n"
          f"----\n{ss_wkt}\n\n"
          "MF-JSON:\n"
          f"--------\n{ss_mfson}\n")

    # Finalize MEOS
    meos_finish()


if __name__ == '__main__':
    main()
