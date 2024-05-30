from cProfile import Profile

from typing import Optional

from domain.Entities.orchestrator import OrchestratorProcess, OrchestratorResult
from domain.ValueObjects.orchestrator import (
    OrchestratorProcessId,
    OrchestratorProcessPid,
    OrchestratorProcessStatus,
    OrchestratorProcessResult,
    OrchestratorProcessException,
    OrchestratorProcessElapsedTime
)


class OrchestratorService:
    """OrchestratorService"""

    def new_process(self, *,
        id: OrchestratorProcessId,
        status: OrchestratorProcessStatus,
        pid: Optional[OrchestratorProcessPid] = None,
    ) -> OrchestratorProcess:

        return OrchestratorProcess(
            id=id,
            status=status,
            pid=pid
        )

    def new_result(self, *,
        id: OrchestratorProcessId,
        status: OrchestratorProcessStatus,
        result: Optional[OrchestratorProcessResult] = None,
        exception: Optional[OrchestratorProcessException] = None,
        elapsed: Optional[OrchestratorProcessElapsedTime] = None
    ) -> OrchestratorResult:

        return OrchestratorResult(
            id=id,
            status=status,
            result=result,
            exception=exception,
            elapsed=elapsed
        )