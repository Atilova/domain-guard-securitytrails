from typing import Protocol, Optional

from domain.Entities.orchestrator import OrchestratorProcess
from domain.ValueObjects.orchestrator import (
    OrchestratorProcessId,
    OrchestratorExecutable,
    OrchestratorOnDoneCallback
)


class IOrchestrator(Protocol):
    """IOrchestrator"""

    def put(self,
        function: OrchestratorExecutable,
        on_done: Optional[OrchestratorOnDoneCallback] = None
    ) -> Optional[OrchestratorProcessId]:
        pass

    def get(self, task_id: OrchestratorProcessId) -> Optional[OrchestratorProcess]:
        pass

    def is_allowed() -> bool:
        pass

    def terminate(self, task_id: OrchestratorProcessId):
        pass

    def terminate_all(self):
        pass
