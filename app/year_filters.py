from fastapi import HTTPException


MIN_YEAR = 1970
MAX_YEAR = 2100


def parse_year_query(year: str | None) -> int:
    if year is None:
        raise HTTPException(
            status_code=400,
            detail="Missing required query parameter: year",
        )

    if not year.isdigit() or len(year) != 4:
        raise HTTPException(
            status_code=400,
            detail="Invalid year format. Expected a 4-digit year, for example 2025",
        )

    return validate_year(int(year))


def validate_year(year: int) -> int:
    if year < MIN_YEAR or year > MAX_YEAR:
        raise HTTPException(
            status_code=400,
            detail=f"year must be between {MIN_YEAR} and {MAX_YEAR}",
        )

    return year


def build_year_filter_params(year: int) -> dict[str, str | int]:
    validated_year = validate_year(year)

    return {
        "created_after": f"{validated_year}-01-01T00:00:00Z",
        "created_before": f"{validated_year + 1}-01-01T00:00:00Z",
        "scope": "all",
        "per_page": 100,
    }
