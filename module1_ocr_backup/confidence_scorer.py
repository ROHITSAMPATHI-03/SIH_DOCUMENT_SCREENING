def calculate_confidence(mrz_data, consistency):

    score = 0

    # ---------------------------------------------
    # MRZ SCORE
    # ---------------------------------------------

    mrz_score = mrz_data.get("mrz_valid_score", 0)

    # PassportEye score is generally 0-100
    if mrz_score >= 80:
        score += 40
    elif mrz_score >= 60:
        score += 30
    elif mrz_score >= 40:
        score += 20
    else:
        score += 10

    # ---------------------------------------------
    # PASSPORT NUMBER
    # ---------------------------------------------

    if mrz_data.get("valid_passport_number"):

        score += 20

    # ---------------------------------------------
    # DATE OF BIRTH
    # ---------------------------------------------

    if mrz_data.get("valid_date_of_birth"):

        score += 15

    # ---------------------------------------------
    # DATE OF EXPIRY
    # ---------------------------------------------

    if mrz_data.get("valid_date_of_expiry"):

        score += 15

    # ---------------------------------------------
    # CONSISTENCY CHECK
    # ---------------------------------------------

    if consistency.get("nationality_match") is True:
        score += 5

    if consistency.get("gender_match") is True:
        score += 5

    # ---------------------------------------------
    # LIMIT SCORE TO 100
    # ---------------------------------------------

    score = min(score, 100)

    # ---------------------------------------------
    # CONFIDENCE LEVEL
    # ---------------------------------------------

    if score >= 85:
        level = "HIGH"

    elif score >= 65:
        level = "MEDIUM"

    else:
        level = "LOW"

    return {
        "score": score,
        "level": level
    }