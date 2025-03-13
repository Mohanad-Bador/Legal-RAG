import subprocess
import threading
from pyngrok import ngrok

def run_fastapi():
    subprocess.run(["uvicorn", "src.apis.main:app", "--host", "0.0.0.0", "--port", "8000"])

def run_streamlit():
    subprocess.run(["streamlit", "run", "src/ui/streamlit.py"])

def run_sqlite_web():
    db_path = "src/database/legal_rag.db"  # Set the path to your SQLite database file
    subprocess.run(["sqlite_web", db_path, "--port", "8081"])

# Start ngrok tunnel for FastAPI
fastapi_tunnel = ngrok.connect(8000)
print("FastAPI URL:", fastapi_tunnel.public_url)

# Start ngrok tunnel for Streamlit
streamlit_tunnel = ngrok.connect(8501)
print("Streamlit URL:", streamlit_tunnel.public_url)

# Start ngrok tunnel for sqlite-web
sqlite_web_tunnel = ngrok.connect(8081)
print("sqlite-web URL:", sqlite_web_tunnel.public_url)

# Run FastAPI in a separate thread
fastapi_thread = threading.Thread(target=run_fastapi)
fastapi_thread.start()

# Run sqlite-web in a separate thread
sqlite_web_thread = threading.Thread(target=run_sqlite_web)
sqlite_web_thread.start()

# Run Streamlit in the main thread
run_streamlit()