import uuid
import os
import aiofiles
from fastapi import UploadFile, HTTPException

from app.core.config import settings


async def save_upload(file: UploadFile) -> str:
    """Guarda la imagen en disco y retorna el nombre de archivo único."""
    ext = os.path.splitext(file.filename or "image.jpg")[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado. Use JPG, PNG o WEBP.")

    filename = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(settings.UPLOADS_DIR, filename)
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_IMAGE_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"Imagen demasiado grande (máx {settings.MAX_IMAGE_SIZE_MB} MB).")

    async with aiofiles.open(dest, "wb") as f:
        await f.write(contents)

    return filename, contents
