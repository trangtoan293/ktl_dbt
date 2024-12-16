from dbt.adapters.spark.connections import SparkConnectionManager  # noqa
from dbt.adapters.spark.connections_custom import MySparkCredentials as SparkCredentials
from dbt.adapters.spark.relation import SparkRelation  # noqa
from dbt.adapters.spark.column import SparkColumn  # noqa
from dbt.adapters.spark.impl_custom import MySparkAdapter as SparkAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import spark

Plugin = AdapterPlugin(
    adapter=SparkAdapter, credentials=SparkCredentials, include_path=spark.PACKAGE_PATH  # type: ignore
)