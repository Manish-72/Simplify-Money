from sentence_transformers import SentenceTransformer
from transformers import pipeline
from .database import files_collection
from .utils import process_csv
from app.models import QueryRequest 

from pydantic import BaseModel
class QueryRequest(BaseModel):
    file_id: str
    query: str

model = SentenceTransformer('all-MiniLM-L6-v2')  # Embeddings
qa_pipeline = pipeline("text-generation", model="google/flan-t5-base")  # LLM

def generate_response(query: str, context: str) -> str:
    prompt = f"Context: {context}\nQuestion: {query}\nAnswer:"
    return qa_pipeline(prompt, max_length=200)[0]['generated_text']


@app.post("/query")
async def query_csv(request: QueryRequest):
    file_data = files_collection.find_one({"file_id": request.file_id})
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Convert CSV data to text for RAG
    context = str(file_data["document"])
    response = generate_response(request.query, context)
    
    return {"response": response}

@app.get("/files")
async def list_files():
    files = list(files_collection.find({}, {"_id": 0, "file_id": 1, "file_name": 1}))
    return {"files": files}

@app.delete("/file/{file_id}")
async def delete_file(file_id: str):
    result = files_collection.delete_one({"file_id": file_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}