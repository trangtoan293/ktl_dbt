from dbt.adapters.spark.python_submissions import *

class SparkSessionPythonJobHelper(PythonJobHelper):

    def __init__(self, parsed_model: Dict, credentials: SparkCredentials) -> None:
        self.credentials = credentials
        self.parsed_model = parsed_model
        self.check_credentials()

    def check_credentials(self) -> None:
        if not self.credentials.server_side_parameters:
            raise ValueError("server_side_parameters is required for spark session submission method.")

    def submit(self, compiled_code: str) -> None:

        spark_configs = " \\\n    ".join(f".config('{parameter}', '{value}')" for parameter, value in self.credentials.server_side_parameters.items())

        compiled_code = f"""
from pyspark.sql import SparkSession
        
spark = SparkSession.builder.enableHiveSupport() \\
    {spark_configs} \\
    .getOrCreate()

{compiled_code}

""".strip()
        
        
        import sys
        import subprocess
        
        try:
            subprocess.run(
                args=[sys.executable, "-c", compiled_code],
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
        
        except subprocess.CalledProcessError as e:
            raise Exception(e.stderr)
