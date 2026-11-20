import pytest

from pymeos import BandStats, Raster
from tests.conftest import TestPyMEOS


class TestRaster(TestPyMEOS):
    """The classes tools/oo_codegen/classgen.py generates for the RASTER family,
    tested as #TestTBox tests a box: each method the object model assigns, an
    operator dispatching on its operand's type and each aggregate over a class's
    values. Each answer is the one MobilityDB's 500_raster test states for the
    same tiles."""

    @staticmethod
    def tiles():
        """The example of the manual: two 2x2 tiles of one 32BF band, the second
        one pixel east and one south of the first, holding 1 and 3."""
        return [
            Raster.make_empty(2, 2, 0, 2, 1, -1, 0, 0, 3857).add_band(1, "32BF", 1, -9999, True),
            Raster.make_empty(2, 2, 1, 1, 1, -1, 0, 0, 3857).add_band(1, "32BF", 3, -9999, True),
        ]

    def test_statistics_of_a_band_span_the_tiles(self):
        stats = Raster.summary_stats_agg(self.tiles(), 1, True)
        assert isinstance(stats, BandStats)
        assert (stats.count(), stats.sum(), stats.mean(), stats.stddev(), stats.min(), stats.max()) == (
            8,
            16,
            2,
            1,
            1,
            3,
        )

    def test_union_takes_the_mean_where_the_tiles_overlap(self):
        # {{1,1,NULL},{1,2,3},{NULL,3,3}}: seven pixels of value, summing to 14.
        union = Raster.raster_union(self.tiles(), 1, "MEAN")
        stats = union.summary_stats(1, True)
        assert (stats.count(), stats.sum(), stats.min(), stats.max()) == (7, 14, 1, 3)

    def test_an_aggregate_over_no_values_is_none(self):
        assert Raster.summary_stats_agg([], 1, True) is None
        assert Raster.raster_union([], 1, "MEAN") is None

    def test_an_operator_dispatches_on_its_operand(self):
        tile = self.tiles()[0]
        assert tile.add(1.5).summary_stats(1, True).mean() == 2.5
        assert tile.add(tile).summary_stats(1, True).mean() == 2
        with pytest.raises(TypeError):
            tile.add("1.5")

    def test_a_writer_takes_its_options(self):
        """A writer of the raster takes its creation options as a list, built as
        #test_statistics_of_a_band_span_the_tiles builds its tiles; GTiff is the
        writer every GDAL MEOS links carries."""
        tile = Raster.make_empty(2, 2, 0, 2, 1, -1, 0, 0, 3857).add_band(1, "8BUI", 7, 0, False)
        assert tile.as_tiff(["TILED=NO"], 3857)[:2] in (b"II", b"MM")
