def validate_table(df):

    rows = len(df)
    cols = len(df.columns)

    if rows < 5:

        return {
            "passed": False,
            "reason": "too_few_rows"
        }

    if cols < 3:

        return {
            "passed": False,
            "reason": "too_few_columns"
        }

    col_headers = sum(
        str(c).startswith("col_")
        for c in df.columns
    )

    if cols > 0:

        unknown_ratio = (
            col_headers / cols
        )

        # if unknown_ratio > 0.7:

        #     return {
        #         "passed": False,
        #         "reason": "weak_headers"
        #     }

    return {
        "passed": True,
        "reason": "ok"
    }