import pytest
from fastapi import HTTPException

from app.year_filters import MAX_YEAR, MIN_YEAR, validate_year, validate_year_value


def test_validate_year_value_accepts_boundary_years():
    assert validate_year_value(MIN_YEAR) == MIN_YEAR
    assert validate_year_value(MAX_YEAR) == MAX_YEAR


def test_validate_year_value_rejects_out_of_range():
    with pytest.raises(ValueError, match="year must be between"):
        validate_year_value(MIN_YEAR - 1)


def test_validate_year_maps_value_error_to_http_400():
    with pytest.raises(HTTPException) as exc_info:
        validate_year(MAX_YEAR + 1)

    assert exc_info.value.status_code == 400
    assert "year must be between" in exc_info.value.detail
