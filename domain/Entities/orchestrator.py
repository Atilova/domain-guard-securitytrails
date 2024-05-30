from datetime import timedelta

from dataclasses import dataclass

from typing import Optional

from domain.ValueObjects.orchestrator import (
    OrchestratorProcessId,
    OrchestratorProcessPid,
    OrchestratorProcessStatus,
    OrchestratorProcessResult,
    OrchestratorProcessException,
    OrchestratorProcessElapsedTime
)


@dataclass
class OrchestratorProcess:
    id: OrchestratorProcessId
    status: OrchestratorProcessStatus
    pid: Optional[OrchestratorProcessPid] = None


@dataclass
class OrchestratorResult:
    id: OrchestratorProcessId
    status: OrchestratorProcessStatus
    result: Optional[OrchestratorProcessResult] = None
    exception: Optional[OrchestratorProcessException] = None
    elapsed: Optional[OrchestratorProcessElapsedTime] = None