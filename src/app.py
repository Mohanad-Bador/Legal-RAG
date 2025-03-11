import subprocess
import threading
from pyngrok import ngrok

def run_fastapi():
    subprocess.run(["uvicorn", "src.fastapi:app", "--host", "0.0.0.0", "--port", "8000"])

def run_streamlit():
    subprocess.run(["streamlit", "run", "src/streamlit.py"])

# Start ngrok tunnel for FastAPI
fastapi_tunnel = ngrok.connect(8000)
print("FastAPI URL:", fastapi_tunnel.public_url)

# Start ngrok tunnel for Streamlit
streamlit_tunnel = ngrok.connect(8501)
print("Streamlit URL:", streamlit_tunnel.public_url)

# Run FastAPI in a separate thread
fastapi_thread = threading.Thread(target=run_fastapi)
fastapi_thread.start()

# Run Streamlit in the main thread
run_streamlit()