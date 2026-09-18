import time
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

LOG_FILE = Path(__file__).with_name("notification.txt")

@app.get("/")
def home():
    return {"message": "Hello, World!"}

def write_notification(message: str):
    print(f"START: {message}", flush=True)
    
    time.sleep(5)  # Simulate a long process
    
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"{message}\n")
        
    print(f"Done: {message}", flush=True)
    
@app.post("/normal")
def normal_notification(message: str):
    write_notification(message)
    return {"message": "Notification written successfully."}

@app.post("/background", status_code=202)
def background_notification(message: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, message)
    return {"message": "Request Accepted."}