import asyncio
from temporalio.client import Client
from temporalio.client import WorkflowFailureError


async def main():
    client = await Client.connect("localhost:7233")

    try:
        result = await client.execute_workflow(
            "RAGAgentWorkflow",
            "Explain how fraud detection works in banking",
            id="rag-agent-workflow-1",
            task_queue="rag-agent-task-queue",
        )
        print("\nFinal Answer:\n", result)
    except WorkflowFailureError as e:
        print("Workflow failed:", e)
        if e.cause:
            print("Cause:", e.cause)


if __name__ == "__main__":
    asyncio.run(main())
