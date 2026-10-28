from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount the root 'static' folder (FastAPI resolves subfolders automatically)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Point Jinja2 to the root 'templates' folder
templates = Jinja2Templates(directory="templates")

# In-memory data store
items_db = [
    {"id": 1, "name": "App Server", "stock": 4},
    {"id": 2, "name": "Load Balancer", "stock": 1},
    {"id": 3, "name": "Cache Cluster", "stock": 9},
]


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
  return templates.TemplateResponse(
      request=request, name="index.html", context={"items": items_db}
  )


@app.post("/items", response_class=RedirectResponse)
async def add_item(name: str = Form(...), stock: int = Form(...)):
  next_id = max([item["id"] for item in items_db], default=0) + 1
  items_db.append({"id": next_id, "name": name, "stock": stock})
  return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
  target = next((item for item in items_db if item["id"] == item_id), None)
  if not target:
    raise HTTPException(status_code=404, detail="Item not found")

  items_db.remove(target)
  return JSONResponse({"status": "success", "deleted_id": item_id})