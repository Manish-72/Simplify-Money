from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Optional
import uuid
import os
from app.database import store_csv, get_db
from app.utils import process_csv
from app.models import CSVFile, QueryRequest, UploadResponse
from app.rag import rag
import json

app = FastAPI(title="RAG CSV Analyzer")

@app.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None)
):
    if not file and not file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either file or file_path must be provided"
        )
    
    file_id = str(uuid.uuid4())
    try:
        processed = process_csv(file or file_path)
        
        # Store in database
        store_csv(
            file_id=file_id,
            file_name=file.filename if file else os.path.basename(file_path),
            document=processed["full_data"],
            metadata={"columns": processed["columns"]}
        )
        
        # Index for RAG
        rag.index_document(file_id, processed["full_data"])
        
        return {
            "file_id": file_id,
            "message": "Upload successful",
            "preview": processed["preview"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/files")
async def list_files():
    db = get_db()
    files = list(db.files.find({}, {"_id": 0, "file_id": 1, "file_name": 1}))
    return {"files": files}

@app.post("/query")
async def query_csv(request: QueryRequest):
    db = get_db()
    file_data = db.files.find_one({"file_id": request.file_id})
    if not file_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if request.stream:
        def generate():
            result = rag.query(request.file_id, request.query)
            yield json.dumps({"response": result["response"]}) + "\n"
            yield json.dumps({"relevant_data": result["relevant_rows"]}) + "\n"
        
        return StreamingResponse(generate(), media_type="application/x-ndjson")
    else:
        result = rag.query(request.file_id, request.query)
        return {
            "response": result["response"],
            "relevant_data": result["relevant_rows"]
        }

@app.delete("/file/{file_id}")
async def delete_file(file_id: str):
    db = get_db()
    result = db.files.delete_one({"file_id": file_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    return {"message": "File deleted successfully"}

# For Streamlit UI
@app.get("/file/{file_id}/preview")
async def get_preview(file_id: str, rows: int = 5):
    db = get_db()
    file_data = db.files.find_one({"file_id": file_id})
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")
    return {"preview": file_data["document"][:rows]}