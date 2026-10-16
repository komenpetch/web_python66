import time
from contextlib import asynccontextmanager, contextmanager

import aiosqlite
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

def load_model():
    print("Loading model...")
    time.sleep(3)
    print("Model loaded.")
    return lambda x: x * 42.0

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code
    print("[STARTUP] preparing system")
    app.state.model = load_model()
    
    db = await aiosqlite.connect("app.db")
    await db.execute(
    """
    CREATE TABLE IF NOT EXISTS prediction_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_val REAL,
        result_val REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )
    
    await db.commit()
    app.state.db = db
    print("[STARTUP] connect SQLite(app.db) successfully")
    
    try:
        yield
    finally:
    
        # shutdown code
        print("[SHUTDOWN] clear model from memory")
        app.state.model = None
        await db.close()
        print("[SHUTDOWN] disconnect SQLite(app.db) successfully")

app = FastAPI(title="Lifespan Demo", lifespan=lifespan)
class PredictIn(BaseModel):
    x: float

@app.get("/")
def read_root():
    return {"message": "Online", 
            "model_loaded": app.state.model is not None,
            "db_connected": app.state.db is not None
            }
    
@app.post("/predict")
async def predict(body: PredictIn):
    model = app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not ready")
    result = model(body.x)
    
    await app.state.db.execute(
        "INSERT INTO prediction_logs(input_val, result_val) VALUES(?, ?)",
        (body.x, result)
    )
    await app.state.db.commit()

    return {"input": body.x, "prediction": result}

@app.get("/logs")
async def get_logs():
    async with app.state.db.execute(
        "SELECT id, input_val, result_val, created_at "
        "FROM prediction_logs ORDER BY id DESC"
        ) as cursor:
        rows = await cursor.fetchall()
    
    logs = [
        {"id": row[0], "input": row[1], "result": row[2], "created_at": row[3]} 
        for row in rows
    ]
    return {"title": len(logs), "logs": logs}