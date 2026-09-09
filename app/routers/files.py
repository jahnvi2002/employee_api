from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException


router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".csv",
    ".xlsx",
    ".jpg",
    ".jpeg",
    ".png"
}


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...)
):
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="File type not allowed"
        )

    # Create uploads folder if it does not exist
    upload_folder = Path("uploads")
    upload_folder.mkdir(exist_ok=True)

    # Create file path
    file_path = upload_folder / file.filename

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "File uploaded successfully"
    }