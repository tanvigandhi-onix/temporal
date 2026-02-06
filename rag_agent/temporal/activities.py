import sys
from pathlib import Path

from temporalio import activity

try:
    from ..agent import ask_rag_agent
except ImportError:
    # Run as script (e.g. python temporal/worker.py from apps/rag_agent)
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from agent import ask_rag_agent


@activity.defn
async def retrieve_and_generate(query: str) -> str:
    """
    Async activity that calls the async RAG agent.
    Fails deterministically on first attempt.
    """

    # Demo failure (first attempt only)
    if activity.info().attempt == 1:
        raise RuntimeError("Simulated transient Vertex AI failure")

    # Properly await async agent
    response = await ask_rag_agent(query)
    return response
