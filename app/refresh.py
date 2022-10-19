import datetime


def refresh():
    """Refreshes key variables to operate without user intervention"""
    date = datetime.datetime.now()
    current_year = date.year
    current_month = date.month
    if current_month < 5:
        current_year -= 1
    summer_fall_s = current_year
    spring_s = current_year + 1

    graduation_years = []
    for i in range(0, 6):
        graduation_years.append(current_year+i)
    graduation_years.append(f"Later than {current_year+i}")

    # TODO hook onto SF for this info
    scholarship_amount = 2500
    scholarship_review_year = "a1R1R000006GXCsUAO"

    updated_vars = {
        "summer_fall_s": summer_fall_s,
        "spring_s": spring_s,
        "graduation_years": graduation_years,
        "graduation_range": range(graduation_years[0], graduation_years[-2]+3),
        "scholarship_amount": scholarship_amount,
        "scholarship_review_year": scholarship_review_year,
        "current_year": f"{str(summer_fall_s)[2:]}-{str(spring_s)[2:]}",
    }

    return updated_vars
