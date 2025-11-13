from typing import Any, Dict

from .log_analyst import LogAnalystAgent


class DispatcherAgent:
    def handle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        agent_type = payload.get("type", "log_analyst")
        if agent_type == "log_analyst":
            agent = LogAnalystAgent()
            return agent.run(payload)
        return {"status": "unknown_agent", "input": payload}
