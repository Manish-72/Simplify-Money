import pandas as pd
from fastapi import HTTPException, UploadFile
from typing import Union, List, Dict
import os
import json

def process_csv(file: Union[UploadFile, str], preview_rows: int = 5) -> dict:
    """Process CSV with preview capability"""
    try:
        if isinstance(file, str):
            if not os.path.exists(file):
                raise HTTPException(status_code=400, detail="File path does not exist")
            df = pd.read_csv(file)
        else:
            df = pd.read_csv(file.file)
        
        # Generate preview
        preview = df.head(preview_rows).fillna("NULL").to_dict(orient="records")
        
        # Full data processing
        full_data = df.fillna("NULL").to_dict(orient="records")
        
        return {
            "full_data": full_data,
            "preview": preview,
            "columns": list(df.columns)
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Empty CSV file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV processing failed: {str(e)}")