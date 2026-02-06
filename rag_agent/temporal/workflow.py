from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import retrieve_and_generate


@workflow.defn
class RAGAgentWorkflow:

    @workflow.run
    async def run(self, query: str) -> str:
        result = await workflow.execute_activity(
            retrieve_and_generate,
            query,
            start_to_close_timeout=timedelta(seconds=120),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=2),
                backoff_coefficient=2.0,
            ),
        )

        return result
