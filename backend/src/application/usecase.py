from src.application.uow_manager import AbstractUoWManager


class Usecase:
    def __init__(
        self,
        uow_manager: AbstractUoWManager,
    ):
        self.uow_manager = uow_manager
