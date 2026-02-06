import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from workflow import RAGAgentWorkflow
import activities


async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="rag-agent-task-queue",
        workflows=[RAGAgentWorkflow],
        activities=[activities.retrieve_and_generate],
    )

    print("Worker started for RAG agent")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
