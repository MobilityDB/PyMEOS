from pymeos import TGeomPointInst, TGeomPointSeq, pymeos_initialize, pymeos_finalize, TGeomPointSeqSet


def main():
    # Initialize session_timezone
    pymeos_initialize()

    # Input temporal points in WKT format
    inst_wkt = "POINT(1 1)@2000-01-01"
    seq_disc_wkt = "{POINT(1 1)@2000-01-01, POINT(2 2)@2000-01-02}"
    seq_linear_wkt = "[POINT(1 1)@2000-01-01, POINT(2 2)@2000-01-02]"
    seq_step_wkt = "Interp=Stepwise;[POINT(1 1)@2000-01-01, POINT(2 2)@2000-01-02]"
    ss_linear_wkt = "{[POINT(1 1)@2000-01-01, POINT(2 2)@2000-01-02],[POINT(3 3)@2000-01-03, POINT(3 3)@2000-01-04]}"
    ss_step_wkt = "Interp=Stepwise;{[POINT(1 1)@2000-01-01, POINT(2 2)@2000-01-02]," \
                  "[POINT(3 3)@2000-01-03, POINT(3 3)@2000-01-04]}"

    # Read WKT into temporal point object
    inst = TGeomPointInst(inst_wkt)
    seq_disc = TGeomPointSeq(seq_disc_wkt)
    seq_linear = TGeomPointSeq(seq_linear_wkt)
    seq_step = TGeomPointSeq(seq_step_wkt)
    ss_linear = TGeomPointSeqSet(ss_linear_wkt)
    ss_step = TGeomPointSeqSet(ss_step_wkt)

    results = [
        ('Temporal Instant', inst_wkt, inst.as_mfjson()),
        ('Temporal Sequence with Discrete Interpolation', seq_disc, seq_disc.as_mfjson()),
        ('Temporal Sequence with Linear Interpolation', seq_linear, seq_linear.as_mfjson()),
        ('Temporal Sequence with Stepwise Interpolation', seq_step, seq_step.as_mfjson()),
        ('Temporal Sequence Set with Linear Interpolation', ss_linear, ss_linear.as_mfjson()),
        ('Temporal Sequence Set with Stepwise Interpolation', ss_step, ss_step.as_mfjson()),
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
    pymeos_finalize()


if __name__ == '__main__':
    main()
