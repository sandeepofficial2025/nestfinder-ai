from google.adk.cli.service_registry import get_service_registry
from google.adk.memory import VertexAiMemoryBankService

def agentengine_memory_factory(uri: str, **kwargs):
    return VertexAiMemoryBankService(
        project="qwiklabs-gcp-03-eb3066a4dd0c",
        location="us-west1",
        agent_engine_id="4169246937456836608"
    )

get_service_registry().register_memory_service("agentengine", agentengine_memory_factory)
