# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import uuid
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    agent_dir = Path(__file__).parent
    yaml_file = agent_dir / "agent_settings.yaml"

    # 1. Load .env (Backward Compatibility)
    if load_dotenv():
        logger.info("✅ Loaded .env file")

    # 2. Load YAML (New Config Format)
    if yaml_file.exists():
        try:
            with open(yaml_file, "r") as f:
                yaml_config = yaml.safe_load(f)
            if yaml_config and isinstance(yaml_config, dict):
                for key, value in yaml_config.items():
                    os.environ[str(key)] = str(value)
                logger.info(f"✅ Loaded YAML config from {yaml_file}")
        except Exception as e:
            logger.error(f"❌ Failed to load YAML config from {yaml_file}: {e}")

load_config()

from contextlib import contextmanager
from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

try:
    from .prompts import return_instructions_root
except ImportError:
    from prompts import return_instructions_root  # loaded as top-level (e.g. from temporal worker)

try:
    from openinference.instrumentation import using_session
except ImportError:
    # Optional: openinference-instrumentation-google-adk not installed (tracing disabled)
    @contextmanager
    def using_session(session_id=None):
        yield
    logger.info("openinference not installed; tracing disabled")


ask_vertex_retrieval = VertexAiRagRetrieval(
    name='retrieve_rag_documentation',
    description=(
        'Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,'
    ),
    rag_resources=[
        rag.RagResource(
            # please fill in your own rag corpus
            # here is a sample rag corpus for testing purpose
            # e.g. projects/123/locations/us-central1/ragCorpora/456
            rag_corpus=os.environ.get("RAG_CORPUS")
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

with using_session(session_id=uuid.uuid4()):
    root_agent = Agent(
        model='gemini-2.0-flash-001',
        name='ask_rag_agent',
        instruction=return_instructions_root(),
        tools=[
            ask_vertex_retrieval,
        ]
    )


async def ask_rag_agent(query: str) -> str:
    """Async entrypoint: run the RAG agent and return the response text."""
    from google.adk.agents.run_config import RunConfig, StreamingMode
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    session_service = InMemorySessionService()
    session = await session_service.create_session(user_id="temporal", app_name="rag_agent")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="rag_agent")
    message = types.Content(role="user", parts=[types.Part.from_text(text=query)])
    parts = []
    async for event in runner.run_async(
        new_message=message,
        user_id="temporal",
        session_id=session.id,
        run_config=RunConfig(streaming_mode=StreamingMode.SSE),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    parts.append(part.text)
    return "\n".join(parts) if parts else "No response from agent."
