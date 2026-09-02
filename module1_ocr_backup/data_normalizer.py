from datetime import datetime


def convert_mrz_date(date_value, date_type=None):
    """
    Convert MRZ YYMMDD format into DD/MM/YYYY.

    MRZ uses two-digit years.
    For passports, years 00-49 are treated as 2000-2049.
    Years 50-99 are treated as 1950-1999.
    """

    if not date_value:
        return None

    try:
        date_value = str(date_value).strip()

        if len(date_value) != 6:
            return None

        year = int(date_value[0:2])
        month = int(date_value[2:4])
        day = int(date_value[4:6])

        # MRZ century rule
        if year >= 50:
            full_year = 1900 + year
        else:
            full_year = 2000 + year

        date = datetime(
            full_year,
            month,
            day
        )

        return date.strftime("%d/%m/%Y")

    except ValueError:
        return None


def normalize_nationality(nationality):

    nationality_map = {
        "IND": "INDIAN",
        "INDIAN": "INDIAN",
        "USA": "AMERICAN",
        "GBR": "BRITISH",
        "CAN": "CANADIAN",
        "AUS": "AUSTRALIAN",
        "DEU": "GERMAN",
        "FRA": "FRENCH",
        "JPN": "JAPANESE"
    }

    if not nationality:
        return None

    nationality = nationality.upper().strip()

    return nationality_map.get(
        nationality,
        nationality
    )