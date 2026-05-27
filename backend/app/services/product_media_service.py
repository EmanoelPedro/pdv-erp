from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings
from app.domain.exceptions import InvalidProductImageError

ALLOWED_IMAGE_TYPES = {
    "image/gif": ".gif",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class ProductMediaService:
    def __init__(self) -> None:
        settings = get_settings()
        self.media_dir = Path(settings.media_dir)
        self.product_dir = self.media_dir / "products"
        self.max_size_bytes = settings.max_product_image_size_bytes

    async def save_product_image(self, upload: UploadFile) -> str:
        content_type = upload.content_type or ""
        extension = ALLOWED_IMAGE_TYPES.get(content_type)
        if extension is None:
            raise InvalidProductImageError(
                "Use uma imagem JPG, PNG, WEBP ou GIF para o produto.",
            )

        payload = await upload.read()
        if not payload:
            raise InvalidProductImageError(
                "Selecione uma imagem valida para o produto.")

        if len(payload) > self.max_size_bytes:
            raise InvalidProductImageError(
                "A imagem do produto excede o limite de 5 MB.")

        self.product_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{uuid4()}{extension}"
        target = self.product_dir / file_name
        target.write_bytes(payload)
        return f"/media/products/{file_name}"

    def delete_product_image(self, image_path: str) -> None:
        relative_path = image_path.removeprefix("/")
        target = Path(relative_path)
        if not target.is_absolute():
            target = Path.cwd() / target

        if target.exists():
            target.unlink()
