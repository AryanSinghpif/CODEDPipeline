def build_metadata(
    table_id,
    table_name,
    page,
    df
):

    return {
        "table_id": table_id,
        "table_name": table_name,
        "page": page,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": "|".join(
            map(
                str,
                df.columns.tolist()
            )
        )
    }