"""
Unit tests for kyte_doolittle and utils modules.

Run with: pytest tests/
"""

import pytest
from src.kyte_doolittle import (
    calculate_hydropathy,
    calculate_hydropathy_window,
    validate_sequence,
    KYTE_DOOLITTLE_SCALE
)
from src.utils import (
    parse_fasta,
    is_uniprot_ac,
    is_uniprot_id,
    detect_sequence_format,
    load_sequence
)


class TestKyteDoolittleScale:
    """Test core hydropathy calculation."""

    def test_validate_sequence_valid(self):
        """Valid sequences should pass."""
        assert validate_sequence("MVLSPADKTVI") == "MVLSPADKTVI"
        assert validate_sequence("mvlspadktvi") == "MVLSPADKTVI"  # lowercase
        assert validate_sequence("MVL SPA\nDKTVI") == "MVLSPADKTVI"  # whitespace

    def test_validate_sequence_invalid(self):
        """Invalid characters should raise ValueError."""
        with pytest.raises(ValueError):
            validate_sequence("MVLSPADKTV1")  # digit
        with pytest.raises(ValueError):
            validate_sequence("MVLSPADKTV@")  # special char

    def test_hydropathy_window_uniform(self):
        """Window with 100% edge weight should be simple average."""
        window = "MVLSPADKT"  # 9 amino acids
        score = calculate_hydropathy_window(window, window_size=9, edge_weight=100)
        expected = sum(KYTE_DOOLITTLE_SCALE[aa] for aa in window) / 9
        assert abs(score - expected) < 0.01

    def test_hydropathy_window_edge_weight_linear(self):
        """Edge weight < 100 with linear model should reduce edge contribution."""
        window = "MVLSPADKT"  # 9 amino acids
        score_100 = calculate_hydropathy_window(window, window_size=9, edge_weight=100, weight_model="linear")
        score_50 = calculate_hydropathy_window(window, window_size=9, edge_weight=50, weight_model="linear")
        # Lower edge weight → different score
        assert score_50 != score_100

    def test_hydropathy_window_edge_weight_exponential(self):
        """Edge weight < 100 with exponential model."""
        window = "MVLSPADKT"  # 9 amino acids
        score_50_linear = calculate_hydropathy_window(
            window, window_size=9, edge_weight=50, weight_model="linear"
        )
        score_50_exp = calculate_hydropathy_window(
            window, window_size=9, edge_weight=50, weight_model="exponential"
        )
        # Different weight models should give different results
        assert score_50_linear != score_50_exp

    def test_calculate_hydropathy_basic(self):
        """Basic hydropathy calculation."""
        seq = "MVLSPADKTNVI"  # 12 amino acids
        scores, meta = calculate_hydropathy(seq, window_size=9)

        # Should have one score per position
        assert len(scores) == len(seq)
        # Metadata should be present
        assert meta['sequence_length'] == len(seq)
        assert meta['window_size'] == 9
        assert -10 < meta['min'] < 10  # Reasonable range
        assert -10 < meta['max'] < 10
        assert meta['mean'] <= meta['max']
        assert meta['mean'] >= meta['min']

    def test_calculate_hydropathy_normalize(self):
        """Normalized scores should be between 0-1."""
        seq = "MVLSPADKTVI"
        scores, meta = calculate_hydropathy(seq, window_size=9, normalize=True)

        for score in scores:
            assert 0 <= score <= 1, f"Score {score} out of [0,1] range"

    def test_calculate_hydropathy_window_sizes(self):
        """Test different window sizes."""
        seq = "MVLSPADKTNVIRAAQNCYSTEIN" * 2  # Long sequence
        for ws in [3, 5, 7, 9, 11, 15, 21]:
            scores, meta = calculate_hydropathy(seq, window_size=ws)
            assert len(scores) == len(seq)
            assert meta['window_size'] == ws

    def test_calculate_hydropathy_edge_weight_range(self):
        """Test edge weights from 0 to 100."""
        seq = "MVLSPADKTNVI"
        scores_0, _ = calculate_hydropathy(seq, window_size=9, edge_weight=0)
        scores_100, _ = calculate_hydropathy(seq, window_size=9, edge_weight=100)
        scores_50, _ = calculate_hydropathy(seq, window_size=9, edge_weight=50)

        # All should be different
        assert scores_0 != scores_100
        assert scores_50 != scores_100

    def test_calculate_hydropathy_short_sequence(self):
        """Short sequence (shorter than window)."""
        seq = "MV"
        with pytest.raises(ValueError):
            calculate_hydropathy(seq, window_size=9)

    def test_calculate_hydropathy_exact_window(self):
        """Sequence exactly matching window size."""
        seq = "MVLSPADKT"  # 9 amino acids
        scores, meta = calculate_hydropathy(seq, window_size=9)
        assert len(scores) == 9


class TestUtilsFunctions:
    """Test utility functions."""

    def test_parse_fasta_valid(self):
        """Valid FASTA should parse."""
        fasta = ">sp|P12345|ABC_HUMAN\nMVLSPA\nDKTVI"
        header, seq = parse_fasta(fasta)
        assert header == "sp|P12345|ABC_HUMAN"
        assert seq == "MVLSPADKTVI"

    def test_parse_fasta_no_header(self):
        """FASTA without header should fail."""
        with pytest.raises(ValueError):
            parse_fasta("MVLSPADKTVI")

    def test_parse_fasta_empty_sequence(self):
        """FASTA with empty sequence should fail."""
        with pytest.raises(ValueError):
            parse_fasta(">header\n")

    def test_is_uniprot_ac(self):
        """Test UniProtKB AC validation."""
        assert is_uniprot_ac("P12345") is True
        assert is_uniprot_ac("Q9Y5K6") is True
        assert is_uniprot_ac("TP53_HUMAN") is False  # ID, not AC
        assert is_uniprot_ac("P1234") is False  # Too short
        assert is_uniprot_ac("P123456") is False  # Too long

    def test_is_uniprot_id(self):
        """Test UniProtKB ID validation."""
        assert is_uniprot_id("TP53_HUMAN") is True
        assert is_uniprot_id("ABC_MOUSE") is True
        assert is_uniprot_id("P12345") is False  # AC, not ID
        assert is_uniprot_id("TP53_HUMAN_EXTRA") is False  # Invalid format

    def test_detect_sequence_format(self):
        """Test sequence format detection."""
        assert detect_sequence_format(">sp|P123|ABC") == "fasta"
        assert detect_sequence_format("P12345") == "uniprot_ac"
        assert detect_sequence_format("TP53_HUMAN") == "uniprot_id"
        assert detect_sequence_format("MVLSPADKTVI") == "raw"

    def test_load_sequence_fasta(self):
        """Load FASTA format."""
        fasta = ">sp|P12345|ABC\nMVLSPA"
        seq, meta = load_sequence(fasta, query_uniprot=False)
        assert seq == "MVLSPA"
        assert meta['source'] == 'fasta'

    def test_load_sequence_raw(self):
        """Load raw sequence."""
        seq, meta = load_sequence("MVLSPADKTVI", query_uniprot=False)
        assert seq == "MVLSPADKTVI"
        assert meta['source'] == 'raw'

    def test_load_sequence_uniprot_disabled(self):
        """UniProtKB query should fail if disabled."""
        with pytest.raises(ValueError):
            load_sequence("P12345", query_uniprot=False)


class TestIntegration:
    """Integration tests combining multiple modules."""

    def test_fasta_to_hydropathy(self):
        """Load FASTA → calculate hydropathy."""
        fasta = ">test\nMVLSPADKTNVI"
        seq, _ = load_sequence(fasta, query_uniprot=False)
        scores, meta = calculate_hydropathy(seq, window_size=9)

        assert len(scores) == len(seq)
        assert meta['sequence_length'] == len(seq)

    def test_parameter_combinations(self):
        """Test various parameter combinations."""
        seq = "MVLSPADKTNVIRAAQNCYSTEIN"
        configs = [
            {"window_size": 9, "edge_weight": 100, "normalize": False},
            {"window_size": 5, "edge_weight": 50, "weight_model": "linear", "normalize": False},
            {"window_size": 11, "edge_weight": 75, "weight_model": "exponential", "normalize": True},
        ]

        for cfg in configs:
            scores, meta = calculate_hydropathy(seq, **cfg)
            assert len(scores) == len(seq), f"Failed for config: {cfg}"
            if cfg.get('normalize'):
                assert all(0 <= s <= 1 for s in scores), f"Normalize failed: {cfg}"


if __name__ == "__main__":
    # Run tests with: pytest tests/test_kyte_doolittle.py -v
    pytest.main([__file__, "-v"])
