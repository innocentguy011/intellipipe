"""
Unit Tests: UDFs
Tests for normalize_category, mask_customer_id, and compute_quality_score UDFs.
Run with: pytest tests/test_udfs.py -v
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from udfs.normalize_category import _normalize_category_impl
from udfs.mask_customer import _mask_customer_id_impl
from udfs.quality_score import _compute_quality_score_impl


# ── normalize_category ────────────────────────────────────────────────────────

class TestNormalizeCategory:
    def test_uppercase_maps_correctly(self):
        assert _normalize_category_impl("ELECTRONICS") == "ELECTRONICS"

    def test_lowercase_with_space_maps_correctly(self):
        assert _normalize_category_impl("electronics ") == "ELECTRONICS"

    def test_abbreviation_maps_correctly(self):
        assert _normalize_category_impl("Elect.") == "ELECTRONICS"

    def test_none_returns_unknown(self):
        assert _normalize_category_impl(None) == "UNKNOWN"

    def test_empty_string_returns_unknown(self):
        assert _normalize_category_impl("") == "UNKNOWN"

    def test_unknown_category_falls_back_to_other(self):
        assert _normalize_category_impl("FURNITURE") == "OTHER"

    def test_home_maps_correctly(self):
        assert _normalize_category_impl("HOME ") == "HOME"

    def test_toys_maps_correctly(self):
        assert _normalize_category_impl("TOYS") == "TOYS"


# ── mask_customer_id ──────────────────────────────────────────────────────────

class TestMaskCustomerId:
    def test_produces_64_char_hex(self):
        result = _mask_customer_id_impl("CUST_12345")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_same_input_same_output(self):
        r1 = _mask_customer_id_impl("CUST_SAME")
        r2 = _mask_customer_id_impl("CUST_SAME")
        assert r1 == r2

    def test_different_input_different_output(self):
        r1 = _mask_customer_id_impl("CUST_A")
        r2 = _mask_customer_id_impl("CUST_B")
        assert r1 != r2

    def test_none_returns_none(self):
        assert _mask_customer_id_impl(None) is None

    def test_empty_string_returns_sha256_of_empty(self):
        result = _mask_customer_id_impl("")
        # SHA-256 of empty string is deterministic
        import hashlib
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected


# ── compute_quality_score ─────────────────────────────────────────────────────

class TestComputeQualityScore:
    def test_perfect_row_scores_one(self):
        score = _compute_quality_score_impl("ORD-1", "CUST-1", 99.99, 2)
        assert score == 1.0

    def test_null_order_id_reduces_score(self):
        score = _compute_quality_score_impl(None, "CUST-1", 99.99, 2)
        assert score == 0.6  # 1.0 - 0.4

    def test_null_customer_id_reduces_score(self):
        score = _compute_quality_score_impl("ORD-1", None, 99.99, 2)
        assert score == 0.7  # 1.0 - 0.3

    def test_negative_price_reduces_score(self):
        score = _compute_quality_score_impl("ORD-1", "CUST-1", -5.00, 2)
        assert score == 0.8  # 1.0 - 0.2

    def test_zero_quantity_reduces_score(self):
        score = _compute_quality_score_impl("ORD-1", "CUST-1", 10.0, 0)
        assert score == 0.9  # 1.0 - 0.1

    def test_score_never_goes_below_zero(self):
        score = _compute_quality_score_impl(None, None, -1.0, 0)
        assert score == 0.0
