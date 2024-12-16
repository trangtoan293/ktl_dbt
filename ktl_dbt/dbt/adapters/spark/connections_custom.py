from dbt.adapters.spark.connections import *

@dataclass
class MySparkCredentials(SparkCredentials):
    streaming_checkpoint_path: Optional[str] = None
