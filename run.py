import uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",  # ➡️ "app.main:app" nghĩa là: lấy biến app trong file main.py thuộc folder app
        host="127.0.0.1",
        port = 8000,
        reload = False, ws_ping_interval =None    
    )
    