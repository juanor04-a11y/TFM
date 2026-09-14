from pyspark.sql import functions as F


def assert_non_empty(
    df,
    dataset_name: str,
) -> int:
    count = df.count()

    if count == 0:
        raise ValueError(
            f"{dataset_name} contains no records."
        )

    return count


def assert_unique_key(
    df,
    key: str,
    dataset_name: str,
) -> None:
    duplicate_count = (
        df
        .groupBy(key)
        .count()
        .filter(
            F.col("count") > 1
        )
        .count()
    )

    if duplicate_count > 0:
        raise ValueError(
            f"{dataset_name} contains "
            f"{duplicate_count} duplicated {key} values."
        )


def assert_no_nulls(
    df,
    column: str,
    dataset_name: str,
) -> None:
    null_count = (
        df
        .filter(
            F.col(column).isNull()
        )
        .count()
    )

    if null_count > 0:
        raise ValueError(
            f"{dataset_name} contains "
            f"{null_count} null values in {column}."
        )