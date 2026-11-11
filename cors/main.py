from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

products_db = [
    {"id": 1, "name": "Iphone", "price": 4000},
    {"id": 2, "name": "Mouse", "price": 1200},
]

class ProductCreate(BaseModel):
    name: str
    price: int
    
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>CORS Demo</title>
    </head>
    <body>
        <h2>CORS Middleware Demo</h2>
        <p>ทดสอบการดึงข้อมูล API ข้ามพอร์ตผ่าน FastAPI</p>
        
        <!-- ปุ่มกดสำหรับเรียกใช้งานฟังก์ชัน JavaScript เพื่อดึงข้อมูล API -->
        <button onclick="getData()">ดึงข้อมูลสินค้า (GET)</button>
        <!-- พื้นที่กล่องข้อความสำหรับแสดงผลลัพธ์ JSON ที่ได้จาก Backend -->
        <pre id="output">รอผลลัพธ์...</pre>

        <script>
            // ฟังก์ชัน JavaScript สำหรับดึงข้อมูลจาก Backend แบบ Asynchronous
            async function getData() {
                try {
                    // ส่งคำขอแบบ GET ไปที่ Endpoint /api/products
                    const res = await fetch('/api/products');
                    // แปลงผลลัพธ์ที่ได้ให้อยู่ในรูปของ JSON
                    const data = await res.json();
                    // นำข้อมูลที่แปลงแล้วมาแสดงผลลงในแท็ก <pre id="output">
                    document.getElementById('output').innerText = "📦 รายการสินค้า:\\n" + JSON.stringify(data, null, 2);
                } catch (err) {
                    // หากเกิดข้อผิดพลาดหรือโดน CORS บล็อก จะแสดงข้อความแจ้งเตือนที่นี่
                    document.getElementById('output').innerText = "CORS Error: " + err;
                }
            }
        </script>
    </body>
    </html>
    """
    
@app.get("/api/products")
def get_products():
    return products_db

@app.post("/api/products")
def add_product(product: ProductCreate):
    new_item = {
        "id": len(products_db) + 1,
        "name": product.name,
        "price": product.price
    }
    products_db.append(new_item)
    return {"status": "success", "added": new_item, "total_items": len(products_db)}