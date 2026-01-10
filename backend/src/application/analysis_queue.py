import asyncio
import contextlib
import logging
from dataclasses import dataclass
from typing import Awaitable, Callable, List

import src.domain.history.entity as history_entity
from src.application.uow_manager import AbstractUoWManager
from src.domain.history.error import StatusUpdateError

logger = logging.getLogger(__name__)


@dataclass
class AnalysisJob:
    history: history_entity.History


class AnalysisQueue:
    def __init__(self, uow_manager: AbstractUoWManager):
        self._uow_manager = uow_manager
        self._queue: asyncio.Queuep[AnalysisJob] = asyncio.Queue()
        self._worker: asyncio.Task = None
        self._handler: Callable[[AnalysisJob], Awaitable[None]] | None = None

    async def start(
        self,
        handler: Callable[[AnalysisJob], Awaitable[None]],
    ) -> None:
        self._handler = handler
        if self._worker is None or self._worker.done():
            self._worker = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._worker:
            self._worker.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._worker
            self._worker = None

    async def enqueue(self, job: AnalysisJob) -> None:
        logger.log(1, f"enqueed job's {job.history.id}")
        await self._queue.put(job)

    async def _run(self):
        if self._handler is None:
            raise "Queue handler must be set before starting"
        try:
            async with self._uow_manager as uow:
                unproccessed_records = await uow.history.get_all_by_status(
                    history_entity.HistoryStatus.PROCESSING.value,
                )
                for record in unproccessed_records:
                    await uow.history.update_status(
                        record.id,
                        history_entity.HistoryStatus.CREATED.value,
                    )
        except Exception as e:
            logger.exception("Failed to set history status '%s'", e)
            raise StatusUpdateError(e)
        async with self._uow_manager as uow:
            created_records: List[
                history_entity.History
            ] = await uow.history.get_all_by_status(
                history_entity.HistoryStatus.CREATED.value,
            )
            created_records.sort(key=lambda record: record.created_at, reverse=True)
            for record in created_records:
                await self.enqueue(AnalysisJob(history=record))
        while True:
            job = await self._queue.get()
            try:
                await self._handler(job)
            except Exception:
                logger.exception("Failed to process analysis job %s", job.history.id)
            finally:
                self._queue.task_done()
