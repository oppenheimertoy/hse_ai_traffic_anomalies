from backend.src.domain.uow import AbstractUnitOfWork


class FileService: 
    async def put_pcap_file(uow: AbstractUnitOfWork, filename: str, file: any ):
        return uow.history