import camelot


def extract_tables(pdf_path):

    results = []

    try:

        tables = camelot.read_pdf(
            pdf_path,
            pages="all",
            flavor="lattice"
        )

    except Exception:

        return []

    for i, table in enumerate(tables):

        try:

            results.append({

                "table_id":
                i + 1,

                "page":
                int(table.page),

                "dataframe":
                table.df

            })

        except Exception:

            continue

    return results