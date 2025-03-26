# RAG CSV ANALYZER - SETUP INSTRUCTIONS

## 1. PREREQUISITES
- Python 3.8 or higher
- MongoDB (local installation or Atlas account)
- Git (optional but recommended)

## 2. CLONE THE REPOSITORY
```sh
git clone https://github.com/yourusername/rag-csv-analyzer.git
cd rag-csv-analyzer
```

## 3. SETUP VIRTUAL ENVIRONMENT
### Windows:
```sh
python -m venv venv
venv\Scripts\activate
```
### Linux/Mac:
```sh
python3 -m venv venv
source venv/bin/activate
```

## 4. INSTALL DEPENDENCIES
```sh
pip install -r requirements.txt
```

## 5. DATABASE SETUP
### A) For Local MongoDB:
- Install MongoDB Community Edition
- Start the service:
  ```sh
  mongod
  ```

### B) For MongoDB Atlas:
- Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
- Get your connection string
- Create a `.env` file with:
  ```sh
  MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net
  ```

## 6. CONFIGURATION
Create a `.env` file in the project root with:
```sh
MONGO_URI=mongodb://localhost:27017  # or your Atlas URI
# Optional:
# DEBUG=True
# PORT=8000
```

## 7. RUN THE APPLICATION
### A) Start FastAPI Backend:
```sh
uvicorn app.main:app --reload
```
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### B) Start Streamlit UI (in a new terminal):
```sh
streamlit run app/ui.py
```
- Web Interface: [http://localhost:8501](http://localhost:8501)

## 8. VERIFY INSTALLATION
1. Upload a test CSV file through the UI
2. Try sample queries like:
   - "What are the key columns?"
   - "Show me summary statistics"

## 9. TROUBLESHOOTING
### Q: MongoDB connection fails?
- Check if `mongod` is running
- Verify `.env` file has the correct URI

### Q: Python package errors?
- Recreate virtual environment:
  ```sh
  rm -rf venv
  python -m venv venv
  source venv/bin/activate  # (or venv\Scripts\activate on Windows)
  pip install -r requirements.txt --force-reinstall
  ```

### Q: Streamlit UI not updating?
- Refresh browser
- Check terminal for errors

## 10. DEPLOYMENT OPTIONS
For production use:
- Dockerize the application
- Use Gunicorn with Uvicorn workers
- Consider cloud platforms:
  - **Backend:** AWS, Azure, Heroku
  - **Database:** MongoDB Atlas
  - **Frontend:** Streamlit Cloud

## Support
For support, contact: `your.email@example.com`

