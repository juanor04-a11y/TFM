import pytest

pyspark = pytest.importorskip("pyspark")
from pyspark.sql import SparkSession

from ott_ticket_intelligence.quality.validators import (
    assert_non_empty,
    assert_no_nulls,
    assert_unique_key,
)


@pytest.fixture(scope="module")
def spark():
    session = SparkSession.builder.master("local[1]").appName("ott-tests").getOrCreate()
    yield session
    session.stop()


def test_assert_non_empty_returns_count(spark):
    df = spark.createDataFrame([("T001",), ("T002",)], ["ticket_id"])

    assert assert_non_empty(df, "tickets") == 2


def test_assert_non_empty_rejects_empty_dataframe(spark):
    df = spark.createDataFrame([], "ticket_id string")

    with pytest.raises(ValueError, match="contains no records"):
        assert_non_empty(df, "tickets")


def test_assert_unique_key_rejects_duplicates(spark):
    df = spark.createDataFrame([("T001",), ("T001",)], ["ticket_id"])

    with pytest.raises(ValueError, match="duplicated"):
        assert_unique_key(df, "ticket_id", "tickets")


def test_assert_no_nulls_rejects_null_values(spark):
    df = spark.createDataFrame([("T001",), (None,)], "ticket_id string")

    with pytest.raises(ValueError, match="null values"):
        assert_no_nulls(df, "ticket_id", "tickets")
