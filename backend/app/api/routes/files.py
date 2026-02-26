"""
APK files API routes: upload, list, download, delete.
"""

from fastapi import APIRouter, Request, UploadFile

from app.core.dependencies import AdminUser, CurrentUser, DbDep
from app.schemas.apk_file import APKFileDetail, APKFileRead
from app.schemas.common import BaseResponse
from app.services.apk_file import APKFileService

router = APIRouter(tags=["APK Files"])


@router.post("/versions/{version_id}/upload", response_model=BaseResponse[APKFileRead], status_code=201)
async def upload_apk(version_id: int, file: UploadFile, db: DbDep, current_user: CurrentUser):
    """Upload an APK file to a version."""
    service = APKFileService(db)
    apk = await service.upload_apk(version_id, file, current_user)
    return BaseResponse.ok(apk)


@router.get("/versions/{version_id}/files", response_model=BaseResponse[list[APKFileDetail]])
def list_files(version_id: int, db: DbDep, _user: CurrentUser):
    """List all APK files for a version."""
    service = APKFileService(db)
    files = service.list_files(version_id)
    return BaseResponse.ok(files)


@router.get("/files/{file_id}/download")
def download_file(file_id: int, request: Request, db: DbDep, _user: CurrentUser):
    """Download an APK file by ID."""
    from app.repositories.download_log import DownloadLogRepository
    
    # Get client IP, handle potential reverse proxy headers
    client_ip = request.headers.get("X-Forwarded-For")
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"
    else:
        # X-Forwarded-For can contain multiple IPs separated by commas
        client_ip = client_ip.split(",")[0].strip()
        
    log_repo = DownloadLogRepository(db)
    log_repo.log_download(file_id, client_ip)
    
    service = APKFileService(db)
    return service.download_file(file_id)


@router.delete("/files/{file_id}", response_model=BaseResponse[None])
def delete_file(file_id: int, db: DbDep, _admin: AdminUser):
    """Delete an APK file. Admin only."""
    service = APKFileService(db)
    service.delete_file(file_id)
    return BaseResponse.ok(None)
