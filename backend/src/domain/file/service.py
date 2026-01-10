import uuid

from src.adapters.storage.minio import MinioStorage
from src.domain.file import entity
from src.domain.file.dto import FileCreateDTO
from src.domain.file.error import FileDownloadError, FileUploadError
from src.domain.uow import AbstractUnitOfWork


class FileService:
    async def __put_pcap_file(
        self,
        storage: MinioStorage,
        filename: str,
        file: bytes,
    ) -> str:
        try:
            return await storage.upload_bytes(filename, file, "pcap", "file/pcap")
        except:  # noqa: E722
            raise FileUploadError

    async def __get_pcap_file(
        self,
        storage: MinioStorage,
        filename: str,
    ) -> tuple[bytes, str]:
        try:
            return await storage.download_bytes(filename)
        except:  # noqa: E722
            raise FileDownloadError

    async def store_file_meta(
        self,
        uow: AbstractUnitOfWork,
        storage: MinioStorage,
        file_dto: FileCreateDTO,
    ) -> entity.File:
        file_id = uuid.uuid4()
        user = await uow.users.get(file_dto.user_id)
        file_url = await self.__put_pcap_file(storage, str(file_id), file_dto.file)
        file_dto.file_url = file_url
        return await uow.files.create(
            file_dto,
            user,
        )

    async def get_file_meta(
        self,
        uow: AbstractUnitOfWork,
        storage: MinioStorage,
        file_id: uuid.UUID,
    ) -> entity.File:
        file_meta: entity.File = await uow.files.get(file_id)
        if not file_meta.deleted:
            file_url = file_meta.file_url
            file = await self.__get_pcap_file(
                storage=storage,
                filename=file_url.split("/")[-1],
            )
        return entity.File(
            id=file_meta.id,
            created_at=file_meta.created_at,
            updated_at=file_meta.updated_at,
            deleted=file_meta.deleted,
            deleted_at=file_meta.deleted_at,
            created_by=file_meta.created_by,
            file_url=file_meta.file_url,
            file=file,
        )
