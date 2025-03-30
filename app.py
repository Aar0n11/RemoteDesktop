from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import pyautogui
import io
import mss
from PIL import Image
import os

app = FastAPI()

# Serve static files (HTML, JS, CSS) from the "static" folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home():
    return FileResponse("static/index.html")  # Serve your HTML file

@app.post("/move-mouse")
async def move_mouse(data: dict):
    if not all(key in data for key in ("x", "y", "screenWidth", "screenHeight")):
        return JSONResponse({"status": "error", "message": "Missing required fields"}, status_code=400)

    x, y = data["x"], data["y"]
    screen_width, screen_height = data["screenWidth"], data["screenHeight"]
    host_width, host_height = pyautogui.size()

    scaled_x = int((x / screen_width) * host_width)
    scaled_y = int((y / screen_height) * host_height)

    pyautogui.moveTo(scaled_x, scaled_y, duration=0.0)
    return {"status": "success", "message": "Mouse moved successfully"}

@app.post("/mousedown")
async def mouse_down():
    pyautogui.mouseDown()
    return {"status": "success", "message": "Mouse button down"}

@app.post("/mouseup")
async def mouse_up():
    pyautogui.mouseUp()
    return {"status": "success", "message": "Mouse button up"}

@app.post("/click")
async def click():
    pyautogui.click()
    return {"status": "success", "message": "Click successful"}

@app.post("/scroll")
async def scroll(data: dict):
    delta_y = data.get("deltaY", 0)
    pyautogui.scroll(-int(delta_y))  # Inverting for correct scrolling behavior
    return {"status": "success", "message": f"Scrolled {delta_y}"}

@app.post("/key")
async def key(data: dict):
    key_value = data.get("key")

    if not key_value:
        return JSONResponse({"status": "error", "message": "Missing key parameter"}, status_code=400)

    pyautogui.press(key_value)
    return {"status": "success", "message": f'Key "{key_value}" pressed'}

@app.get("/screenshot")
async def screenshot():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

        img_io = io.BytesIO()
        img.save(img_io, format="JPEG", quality=20)
        img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
