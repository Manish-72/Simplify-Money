from pydantic import BaseModel
from typing import List, Dict, Optional

class CSVFile(BaseModel):
    file_id: str
    file_name: str
    document: List[Dict[str, str]]  # CSV rows as dicts
    metadata: Optional[dict] = None

class QueryRequest(BaseModel):
    file_id: str
    query: str
    stream: Optional[bool] = False

class UploadResponse(BaseModel):
    file_id: str
    message: str
    preview: Optional[List[Dict]] = None