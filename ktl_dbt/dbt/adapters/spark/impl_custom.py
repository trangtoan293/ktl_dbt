from dbt.adapters.spark.impl import *
from dbt.adapters.spark.python_submissions_custom import SparkSessionPythonJobHelper

class MySparkAdapter(SparkAdapter):
    
    @property
    def default_python_submission_method(self) -> str:
        return "spark_session"

    @property
    def python_submission_helpers(self) -> Dict[str, Type[PythonJobHelper]]:
        return {
            "job_cluster": JobClusterPythonJobHelper,
            "all_purpose_cluster": AllPurposeClusterPythonJobHelper,
            "spark_session": SparkSessionPythonJobHelper,
        }
