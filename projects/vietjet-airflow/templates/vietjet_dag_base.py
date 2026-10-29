"""
Vietjet Airflow Standard DAG Template.
Used by DagCoder subagent as reference implementation for generating production-ready DAGs.
"""

from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.models import Variable
from airflow.operators.python import get_current_context
from datetime import datetime
import pendulum

# Timezone standard
local_tz = pendulum.timezone("Asia/Ho_Chi_Minh")
default_date_from = pendulum.now(local_tz).subtract(days=1).to_date_string()
default_date_to = pendulum.now(local_tz).to_date_string()

# Connections
# HOOK_POSTGRES = 'vietjet_db'
# HOOK_SFTP = 'sftp_conn'

default_args = {
    "owner": "data_engineer",
    "depends_on_past": False,
    "email": ["data.platform@vietjetair.com"],
    "email_on_failure": False,
    "retries": 1,
}

@dag(
    dag_id="template_dag_id",
    default_args=default_args,
    description="Standard Vietjet Data Pipeline DAG",
    schedule="0 2 * * *",
    start_date=datetime(2025, 1, 1, tzinfo=local_tz),
    catchup=False,
    tags=["vietjet", "etl", "taskflow"],
    params={
        "date_from": Param(default_date_from, type="string", format="date"),
        "date_to": Param(default_date_to, type="string", format="date"),
    },
)
def template_pipeline():

    @task
    def get_run_params() -> dict:
        context = get_current_context()
        dag_run = context.get("dag_run")
        p_from = default_date_from
        p_to = default_date_to
        if dag_run and dag_run.conf:
            p_from = dag_run.conf.get("date_from", p_from)
            p_to = dag_run.conf.get("date_to", p_to)
        return {"date_from": p_from, "date_to": p_to}

    @task
    def extract_data(params: dict):
        # Extract logic using hooks e.g. PostgresHook, OracleHook, etc.
        pass

    @task
    def transform_and_load(raw_data: any):
        # Transformation and delivery
        pass

    # Execution flow
    p = get_run_params()
    data = extract_data(p)
    transform_and_load(data)

dag_instance = template_pipeline()
