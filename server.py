import asyncio
import json
import threading
import requests
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from config import GEMINI_API_KEY, OPENWEATHER_API_KEY
from agents.orchestrator import Orchestrator
from google import genai

app = FastAPI(title="Quy Nhơn Smart Travel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory queues for streaming tasks
tasks: Dict[str, asyncio.Queue] = {}

class PlanRequest(BaseModel):
    destination: str = "Quy Nhơn"
    days: int = 3
    budget_per_day: int = 2000000
    has_kids: bool = False
    language: str = "Tiếng Việt"
    preferences: str = ""
    weather_sim_mode: str = "Nắng đẹp"

class ChatRequest(BaseModel):
    message: str
    language: str = "vi"
    context: str = ""

@app.post("/api/plan")
async def start_plan(req: PlanRequest):
    import uuid
    task_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    tasks[task_id] = queue
    main_loop = asyncio.get_running_loop()
    
    def run_orchestrator():
        try:
            def on_update(log_entry):
                main_loop.call_soon_threadsafe(queue.put_nowait, {
                    "type": "log",
                    "data": log_entry
                })

            orchestrator = Orchestrator(
                gemini_key=GEMINI_API_KEY,
                weather_key=OPENWEATHER_API_KEY
            )
            
            final_state = orchestrator.run(
                destination=req.destination,
                days=req.days,
                budget_per_day=req.budget_per_day,
                language=req.language,
                has_kids=req.has_kids,
                preferences=req.preferences,
                weather_sim_mode=req.weather_sim_mode,
                on_state_update=on_update
            )
            
            main_loop.call_soon_threadsafe(queue.put_nowait, {
                "type": "result",
                "data": final_state
            })
        except Exception as e:
            main_loop.call_soon_threadsafe(queue.put_nowait, {
                "type": "error",
                "data": str(e)
            })
        finally:
            main_loop.call_soon_threadsafe(queue.put_nowait, {"type": "done"})
            
    thread = threading.Thread(target=run_orchestrator)
    thread.start()
    
    return {"task_id": task_id}

@app.get("/api/stream/{task_id}")
async def stream_plan(task_id: str):
    if task_id not in tasks:
        return {"error": "Task not found"}
        
    queue = tasks[task_id]
    
    async def event_generator():
        while True:
            event = await queue.get()
            if event["type"] == "done":
                if task_id in tasks:
                    del tasks[task_id]
                break
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/chat")
async def chat_with_ai(req: ChatRequest):
    """AI chatbot endpoint for Quy Nhon travel questions."""
    try:
        if not GEMINI_API_KEY:
            return JSONResponse({"reply": "API key chưa được cấu hình. Vui lòng thêm GEMINI_API_KEY vào .env"}, status_code=200)
        
        lang_map = {
            "vi": "Tiếng Việt",
            "en": "English",
            "ja": "Japanese (日本語)",
            "ko": "Korean (한국어)"
        }
        response_lang = lang_map.get(req.language, "Tiếng Việt")
        
        system_prompt = f"""Bạn là AI trợ lý du lịch thông minh chuyên về Quy Nhơn, Bình Định, Việt Nam.
Bạn biết rất nhiều về:
- Các địa điểm nổi tiếng: Kỳ Co, Eo Gió, Hòn Khô, Ghềnh Ráng, Tháp Đôi, Cầu Thị Nại
- Ẩm thực địa phương: bánh xèo tôm nhảy, chả ram tôm đất, bún chả cá, cháo sứa
- Khách sạn và homestay các phân khúc
- Thời tiết và mùa du lịch
- Tips và lưu ý cho khách du lịch
- Văn hóa và phong tục địa phương
Trả lời bằng {response_lang}. Câu trả lời ngắn gọn, thân thiện, có emoji, phong cách GenZ nhưng vẫn thông tin đầy đủ.
"""
        
        from agents.gemini_helper import GeminiHelper
        helper = GeminiHelper(
            api_key=GEMINI_API_KEY, 
            model_name="gemini-flash-latest", 
            system_instruction=system_prompt
        )
        
        full_prompt = req.message
        if req.context:
            full_prompt = f"Context: {req.context}\n\nCâu hỏi: {req.message}"
        
        reply = helper.generate_text(full_prompt)
        if not reply:
            reply = "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này."
        
        return JSONResponse({"reply": reply, "language": req.language})
        
    except Exception as e:
        print(f"Chat error: {e}")
        error_messages = {
            "vi": "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại!",
            "en": "Sorry, an error occurred. Please try again!",
            "ja": "申し訳ありません、エラーが発生しました。もう一度お試しください！",
            "ko": "죄송합니다, 오류가 발생했습니다. 다시 시도해 주세요!"
        }
        return JSONResponse({"reply": error_messages.get(req.language, "Error occurred"), "language": req.language})

@app.get("/api/weather/quynhon")
async def get_quy_nhon_weather():
    """Fetch live weather for Quy Nhon."""
    QUY_NHON_LAT = 13.7765
    QUY_NHON_LON = 109.2342
    
    if OPENWEATHER_API_KEY:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={QUY_NHON_LAT}&lon={QUY_NHON_LON}&appid={OPENWEATHER_API_KEY}&units=metric&lang=vi"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                condition = data["weather"][0]["description"].title()
                icon = data["weather"][0]["icon"]
                wind_speed = data["wind"]["speed"]
                
                return JSONResponse({
                    "success": True,
                    "temp": round(temp),
                    "feels_like": round(feels_like),
                    "humidity": humidity,
                    "condition": condition,
                    "icon": f"https://openweathermap.org/img/wn/{icon}@2x.png",
                    "wind_speed": wind_speed,
                    "location": "Quy Nhơn, Bình Định"
                })
        except Exception as e:
            print(f"Weather fetch error: {e}")
    
    # Mock data fallback
    import random
    conditions = [
        {"cond": "Nắng đẹp ☀️", "temp": 31, "icon": "https://openweathermap.org/img/wn/01d@2x.png"},
        {"cond": "Mây rải rác ⛅", "temp": 29, "icon": "https://openweathermap.org/img/wn/02d@2x.png"},
        {"cond": "Mưa nhẹ 🌦️", "temp": 26, "icon": "https://openweathermap.org/img/wn/09d@2x.png"},
    ]
    mock = random.choice(conditions)
    return JSONResponse({
        "success": True,
        "temp": mock["temp"],
        "feels_like": mock["temp"] - 2,
        "humidity": random.randint(65, 85),
        "condition": mock["cond"],
        "icon": mock["icon"],
        "wind_speed": round(random.uniform(2, 8), 1),
        "location": "Quy Nhơn, Bình Định",
        "is_mock": True
    })

@app.get("/api/forecast/quynhon")
async def get_quy_nhon_forecast():
    """Fetch 5-day weather forecast for Quy Nhon."""
    QUY_NHON_LAT = 13.7765
    QUY_NHON_LON = 109.2342
    
    if OPENWEATHER_API_KEY:
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={QUY_NHON_LAT}&lon={QUY_NHON_LON}&appid={OPENWEATHER_API_KEY}&units=metric&lang=vi&cnt=40"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                # Process daily forecast (take one entry per day)
                daily = {}
                for item in data["list"]:
                    date = item["dt_txt"][:10]
                    if date not in daily:
                        daily[date] = {
                            "date": date,
                            "temp_max": item["main"]["temp_max"],
                            "temp_min": item["main"]["temp_min"],
                            "condition": item["weather"][0]["description"].title(),
                            "icon": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                            "rain_prob": item.get("pop", 0)
                        }
                return JSONResponse({"success": True, "forecast": list(daily.values())[:5]})
        except Exception as e:
            print(f"Forecast error: {e}")
    
    # Mock 5-day forecast
    import random
    from datetime import date, timedelta
    forecast = []
    for i in range(5):
        d = date.today() + timedelta(days=i)
        rain = random.random() < 0.3
        forecast.append({
            "date": d.isoformat(),
            "temp_max": random.randint(28, 34),
            "temp_min": random.randint(24, 28),
            "condition": "Mưa nhẹ" if rain else "Nắng đẹp",
            "icon": "https://openweathermap.org/img/wn/09d@2x.png" if rain else "https://openweathermap.org/img/wn/01d@2x.png",
            "rain_prob": round(random.uniform(0.6, 0.9), 2) if rain else round(random.uniform(0.0, 0.2), 2)
        })
    return JSONResponse({"success": True, "forecast": forecast, "is_mock": True})

@app.get("/api/places")
async def get_places():
    """Return all Quy Nhon places data."""
    import os
    data_path = os.path.join(os.path.dirname(__file__), "data", "places_data.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse({"success": True, "places": data.get("Quy Nhơn", [])})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@app.get("/api/restaurants")
async def get_restaurants():
    """Return all Quy Nhon restaurants data."""
    import os
    data_path = os.path.join(os.path.dirname(__file__), "data", "restaurants_data.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse({"success": True, "restaurants": data.get("Quy Nhơn", [])})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@app.get("/api/hotels")
async def get_hotels():
    """Return all Quy Nhon hotels data."""
    import os
    data_path = os.path.join(os.path.dirname(__file__), "data", "booking_data.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        dest_data = data.get("Quy Nhơn", {})
        return JSONResponse({
            "success": True,
            "hotels": dest_data.get("accommodations", []),
            "transports": dest_data.get("transports", [])
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

# Mount static files LAST
import os
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
