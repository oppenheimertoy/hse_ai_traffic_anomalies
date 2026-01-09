from typing import Callable
from uuid import UUID

import src.domain.history.entity as entity
from src.application.analysis_queue import AnalysisJob, AnalysisQueue
from src.application.uow_manager import AbstractUoWManager
from src.domain.history.dto import (
    HistoryCreateDTO,
    HistoryProcessDTO,
    HistoryStatus,
    HistoryUpdateDTO,
)
from src.domain.history.error import FileProcessingError, StatusUpdateError
from src.domain.uow import AbstractUnitOfWork

from core.time_series.wrapper import AnomaliesDetector


class HistoryService:
    def __init__(
        self,
        queue: AnalysisQueue,
        uow_manager_factory: Callable[[], AbstractUoWManager],
        ts_detector: AnomaliesDetector,
    ):
        self._queue = queue
        self._uow_manager_factory = uow_manager_factory
        self._ts_detector = ts_detector

    async def create_history(
        self,
        uow: AbstractUnitOfWork,
        create_dto: HistoryCreateDTO,
    ) -> entity.History:
        return await uow.history.create(create_dto)

    async def process_job(
        self,
        job: AnalysisJob,
    ) -> None:
        uow_manager = self._uow_manager_factory()
        try:
            async with uow_manager as uow:
                await self._set_status(uow, job.history.id, HistoryStatus.PROCESSING)
                await uow_manager.commit()
        except Exception as e:
            raise StatusUpdateError(e)
        update_dto = HistoryUpdateDTO(
            user_id=job.history.user_id,
            status=job.history.status.value,
            id=job.history.id,
            error=None,
            result=None,
        )
        try:
            detector_results = self._ts_detector.detect(job.history.file_url)
        except Exception as e:
            async with uow_manager as uow:
                await self._set_status(uow, job.history.id, HistoryStatus.ERROR)
                update_dto.error = str(e)
                update_dto.status = HistoryStatus.ERROR.value
                await self._set_error(uow, update_dto)
                await uow_manager.commit()
            raise FileProcessingError

        async with uow_manager as uow:
            update_dto.result = str(detector_results)
            update_dto.status = HistoryStatus.DONE.value
            await uow.history.update(update_dto.id, update_dto)
            await uow_manager.commit()

    async def push_history_to_queue(self, history: entity.History) -> None:
        await self._queue.enqueue(
            AnalysisJob(
                history=history,
            ),
        )

    async def _set_status(
        self,
        uow: AbstractUnitOfWork,
        history_id: UUID,
        history_status: entity.HistoryStatus,
    ) -> entity.History:
        return await uow.history.update_status(history_id, history_status.value)

    async def _set_error(
        self,
        uow: AbstractUnitOfWork,
        history: HistoryUpdateDTO,
    ) -> entity.History:
        return await uow.history.update(history.id, history)
