import logging

from uuid import uuid4
from signal import SIGTERM
from os import getpid, kill
from functools import partial
from timeit import default_timer as timer
from datetime import timedelta
from multiprocessing import Pool, Manager

from typing import (
    Protocol,
    Optional,
    TypedDict,
    Callable,
    Any
)

from utils.dictget import dictget
from utils.notnone import notnone_init

from domain.Entities.orchestrator import OrchestratorProcess, OrchestratorResult
from domain.Enums.orchestrator import ProcessStatus as Status
from domain.ValueObjects.orchestrator import (
    OrchestratorProcessId,
    OrchestratorExecutable,
    OrchestratorOnDoneCallback,
    OrchestratorProcessPid,
    OrchestratorProcessStatus,
    OrchestratorProcessResult,
    OrchestratorProcessException,
    OrchestratorProcessElapsedTime
)


logger = logging.getLogger('Orchestrator')


TaskId = str

class TaskDict(TypedDict):
    """TaskDict"""

    id: TaskId
    status: Status
    pid: Optional[int]
    result: Optional[str]
    exception: Optional[Exception]
    elapsed: Optional[timedelta]

Tasks = dict[TaskId, TaskDict]
Function = Callable[[], Any]
OnDoneCallback = Callable[[Any], None]
CleanUpCallback = Callable[[Any], None]
ResultMapper = Callable[[TaskDict], Any]


def _is_pending(task: TaskDict):
    """_is_pending"""

    return task['status'] == Status.PENDING

def _is_executing(task: TaskDict):
    """_is_executing"""

    return task['status'] == Status.EXECUTING

def _is_canceled(task: TaskDict):
    """_is_canceled"""

    return task['status'] == Status.CANCELED

def _is_aborted(task: TaskDict):
    """_is_aborted"""

    return task['status'] == Status.ABORTED

def _is_task_alive(task: TaskDict):
    """_is_process_alive"""

    return _is_pending(task) or _is_executing(task)

def _is_task_stopped(task: TaskDict):
    """_is_task_stopped"""

    return _is_canceled(task) or _is_aborted(task)

def _alive_tasks(tasks: Tasks):
    """_alive_tasks"""

    filtered_alive = filter(_is_task_alive, tasks.values())
    return sum(1 for _ in filtered_alive)

def _is_within_alive_limit(limit: int):
    """_is_within_alive_limit"""

    return lambda tasks: _alive_tasks(tasks) < limit

def _kill_process(pid: int):
    """_kill_process"""

    kill(pid, SIGTERM)

def _on_done_mock(*args, **kwargs):
    """_on_done_mock"""

def _get_on_done_callback(callback: Optional[OrchestratorOnDoneCallback]) -> OnDoneCallback:
    """_on_done_callback"""

    return callback is not None and callback.raw() or _on_done_mock

def _process(task: TaskDict, function: Function):
    """_process"""

    if _is_canceled(task): return task

    task['pid'] = getpid()
    task['status'] = Status.EXECUTING

    started = timer()
    try:
        result = function()
        elapsed = timedelta(seconds=timer()-started)
        task['result'] = result
        task['status'] = Status.DONE
    except Exception as exp:
        elapsed = timedelta(seconds=timer()-started)
        task['exception'] = exp
        task['status'] = Status.FAILED
        logger.exception('Process failed.')
    finally:
        task['elapsed'] = elapsed

    return task

def _process_fulfilled(task: TaskDict, *, clean_up: CleanUpCallback, mapper: ResultMapper, callback: OnDoneCallback):
    """_process_fulfilled"""

    if _is_canceled(task): return clean_up(task)

    mapped = mapper(task)
    try:
        callback(mapped)
    except Exception as exp:
        logger.exception('Process on_done callback failed to execute.')

    clean_up(task)


class IOrchestratorService(Protocol):
    """IOrchestratorService"""

    def new_process(self, *,
        id: OrchestratorProcessId,
        status: OrchestratorProcessStatus,
        pid: Optional[OrchestratorProcessPid] = None,
    ) -> OrchestratorProcess:
        pass

    def new_result(self, *,
        id: OrchestratorProcessId,
        status: OrchestratorProcessStatus,
        result: Optional[OrchestratorProcessResult] = None,
        exception: Optional[OrchestratorProcessException] = None,
        elapsed: Optional[OrchestratorProcessElapsedTime] = None
    ) -> OrchestratorResult:
        pass


class ProcessOrchestrator:
    """ProcessOrchestrator"""

    def __init__(self, service: IOrchestratorService, workers=3, max_tasks=5):
        # Todo: add process execution timeout
        self.__tasks: Tasks = {}
        self.__service = service
        self.__is_within_limit = _is_within_alive_limit(max_tasks)

        self.__manager = Manager()
        self.__pool = Pool(processes=workers)

    def put(self,
        function: OrchestratorExecutable,
        on_done: Optional[OrchestratorOnDoneCallback] = None
    ) -> Optional[OrchestratorProcessId]:
        # Todo: add on stopped_callback in future to receive ABORTED or CANCELED
        if not self.is_allowed(): return

        task_id: TaskId = uuid4().hex
        task: TaskDict = self.__manager.dict({
            'id': task_id,
            'status': Status.PENDING,
            'pid': None,
            'result': None,
            'exception': None,
            'elapsed': None
        })

        self.__tasks[task_id] = task

        on_done_callback = _get_on_done_callback(on_done)
        callback = partial(
            _process_fulfilled,
            mapper=self.__map_result,
            clean_up=self.__clean_up,
            callback=on_done_callback
        )

        self.__pool.apply_async(func=_process, args=(task, function.raw()), callback=callback)

        return OrchestratorProcessId(task_id)

    def get(self, task_id: OrchestratorProcessId) -> Optional[OrchestratorProcess]:
        task = self.__tasks.get(task_id.raw())
        if task is None: return

        status, pid = dictget(task, 'status', 'pid')
        return self.__service.new_process(
            id=OrchestratorProcessId(task_id),
            status=OrchestratorProcessStatus(status),
            pid=notnone_init(pid, OrchestratorProcessPid)
        )

    def is_allowed(self) -> bool:
        return self.__is_within_limit(self.__tasks)

    def terminate(self, task_id: OrchestratorProcessId):
        task = self.__tasks.get(task_id.raw())
        if task is None or _is_task_stopped(task): return

        pid, = dictget(task, 'pid')

        # Todo: add on stopped_callback in future to receive ABORTED or CANCELED
        if pid is None:
            task['status'] = Status.CANCELED
            return

        _kill_process(pid)
        task['status'] = Status.ABORTED
        self.__clean_up(task)

    def terminate_all(self):
        self.__pool.terminate()
        self.__tasks = {}

    def __clean_up(self, task: TaskDict):
        self.__tasks.pop(task['id'])

    def __map_result(self, task: TaskDict) -> OrchestratorResult:
        id, status, result, exception, elapsed = dictget(task, 'id', 'status', 'result', 'exception', 'elapsed')

        return self.__service.new_result(
            id=OrchestratorProcessId(id),
            status=OrchestratorProcessStatus(status),
            result=notnone_init(result, OrchestratorProcessResult),
            exception=notnone_init(exception, OrchestratorProcessException),
            elapsed=notnone_init(elapsed, OrchestratorProcessElapsedTime)
        )