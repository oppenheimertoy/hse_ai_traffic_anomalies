import asyncio
from io import BytesIO
from typing import Tuple

from minio import Minio


class MinioStorage:

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False,
    ) -> None:
        self._client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self._bucket = bucket

    def _ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    async def upload_bytes(
        self,
        object_name: str,
        content: bytes,
        content_type: str = "file/pcap",
    ) -> str:
        def _upload() -> str:
            self._ensure_bucket()
            self._client.put_object(
                bucket_name=self._bucket,
                object_name=object_name,
                data=BytesIO(content),
                length=len(content),
                content_type=content_type,
            )
            return self._client.get_presigned_url(
                method="GET",
                bucket_name=self._bucket,
                object_name=object_name,
            )

        return await asyncio.to_thread(_upload)

    async def download_bytes(self, object_name: str) -> Tuple[bytes, str]:
        def _download() -> Tuple[bytes, str]:
            response = self._client.get_object(self._bucket, object_name)
            try:
                data = response.read()
                content_type = response.headers.get("Content-Type", "file/pcap")
            finally:
                response.close()
                response.release_conn()
            return data, content_type

        return await asyncio.to_thread(_download)
