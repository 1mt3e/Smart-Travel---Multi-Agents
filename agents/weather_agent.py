import json
import random
import requests
from config import UTILITY_MODEL
from agents.gemini_helper import GeminiHelper

class WeatherAgent:
    def __init__(self, weather_key=None, gemini_key=None):
        self.weather_key = weather_key
        self.gemini_key = gemini_key
        self.model = None
        if self.gemini_key:
            self.model = GeminiHelper(
                api_key=self.gemini_key,
                model_name=UTILITY_MODEL,
                system_instruction=(
                    "Bạn là một Weather Advisor du lịch thông minh. Khi một địa điểm ngoài trời có thời tiết xấu (mưa bão), "
                    "hãy đề xuất hoạt động hoặc địa điểm thay thế trong nhà (indoor) hoặc gần đó, an toàn và thú vị."
                ),
            )

    def fetch_real_weather(self, lat, lon):
        """Fetches real weather from OpenWeatherMap API."""
        if not self.weather_key:
            return None
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.weather_key}&units=metric&lang=vi"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                temp = data.get("main", {}).get("temp", 28)
                condition = data.get("weather", [{}])[0].get("description", "Không rõ")
                # Estimate rain probability based on condition text or clouds
                clouds = data.get("clouds", {}).get("all", 0)
                main_cond = data.get("weather", [{}])[0].get("main", "Clear")
                
                rain_prob = 0.0
                if main_cond in ["Rain", "Drizzle", "Thunderstorm"]:
                    rain_prob = 0.85
                elif clouds > 70:
                    rain_prob = 0.40
                
                return {
                    "temp": round(temp),
                    "condition": condition.capitalize(),
                    "rain_prob": rain_prob
                }
        except Exception as e:
            print(f"Error calling Weather API: {e}")
        return None

    def get_mock_weather(self, place_name, sim_mode):
        """Generates realistic weather data for simulation during demos."""
        if sim_mode == "Nắng đẹp":
            return {
                "temp": random.randint(29, 33),
                "condition": "Nắng ráo, trời quang đãng",
                "rain_prob": round(random.uniform(0.0, 0.15), 2)
            }
        elif sim_mode == "Mưa lớn (Demo Cảnh báo)":
            # For outdoor/nature spots, simulate rain; others, make overcast
            outdoor_keywords = ["kỳ co", "eo gió", "hòn khô", "biển hồ", "núi lửa", "thác", "đồi cát", "đồi chè"]
            is_outdoor = any(kw in place_name.lower() for kw in outdoor_keywords)
            if is_outdoor:
                return {
                    "temp": random.randint(23, 25),
                    "condition": "Mưa dông lớn, nguy cơ dông sét",
                    "rain_prob": round(random.uniform(0.75, 0.95), 2)
                }
            else:
                return {
                    "temp": random.randint(25, 27),
                    "condition": "Trời âm u, nhiều mây, mưa nhẹ",
                    "rain_prob": round(random.uniform(0.40, 0.60), 2)
                }
        else: # Ngẫu nhiên
            conds = [
                ("Nắng nhẹ, mây rải rác", 0.1, 28, 31),
                ("Trời nhiều mây, dịu mát", 0.3, 26, 29),
                ("Mưa rào rải rác", 0.7, 24, 27),
                ("Nắng nóng gay gắt", 0.0, 32, 35)
            ]
            choice = random.choice(conds)
            return {
                "temp": random.randint(choice[2], choice[3]),
                "condition": choice[0],
                "rain_prob": choice[1]
            }

    def suggest_alternative(self, place_name, original_description, condition):
        """Uses LLM to rewrite a rain-affected activity with an indoor/safe alternative."""
        if not self.gemini_key:
            return "Hãy chuyển sang hoạt động trong nhà gần đó hoặc quán cà phê văn hóa địa phương để tránh mưa."

        prompt = f"""
Địa điểm du lịch ngoài trời: "{place_name}"
Hoạt động dự kiến gốc: "{original_description}"
Tình trạng thời tiết hiện tại: "{condition}" (mưa lớn nguy hiểm)

Hãy gợi ý 1 giải pháp thay thế cụ thể (ví dụ: ghé thăm bảo tàng, chùa chiền có mái che lân cận, hoặc trải nghiệm cà phê đặc sản trong nhà ở khu vực đó).
Hãy đưa ra câu trả lời ngắn gọn dưới 3 câu, thiết thực và rõ ràng cho du khách.
"""
        try:
            return self.model.generate_text(prompt)
        except Exception as e:
            print(f"Error calling Gemini in WeatherAgent: {e}")
            return "Nên hoãn tham quan ngoài trời, ghé thăm quán cà phê ấm cúng ven biển hoặc bảo tàng thành phố để nghỉ ngơi tránh mưa."

    def run(self, state):
        """Reads itinerary, queries/simulates weather for each place, notes alerts and alternatives."""
        sim_mode = state["user_request"].get("weather_sim_mode", "Nắng đẹp")
        
        alerts = []
        raw_weather_data = {}

        for item in state["itinerary"]:
            day = item["day"]
            session = item["session"]
            places = item.get("places", [])

            for place in places:
                name = place["name"]
                coord = place.get("coordinate", {})
                lat = coord.get("lat")
                lon = coord.get("lon")

                # Try fetching real weather, fallback to mock simulation
                weather_info = None
                if self.weather_key and lat and lon:
                    weather_info = self.fetch_real_weather(lat, lon)
                
                if not weather_info:
                    weather_info = self.get_mock_weather(name, sim_mode)

                raw_weather_data[name] = weather_info

                # If rain probability is high (>= 60%), generate warning and alternative activity
                if weather_info["rain_prob"] >= 0.60:
                    alternative = self.suggest_alternative(name, place.get("description", ""), weather_info["condition"])
                    alert_entry = {
                        "day": day,
                        "session": session,
                        "place": name,
                        "alert": True,
                        "warning": f"Cảnh báo thời tiết: {weather_info['condition']} (Khả năng mưa {int(weather_info['rain_prob']*100)}%, nhiệt độ {weather_info['temp']}°C).",
                        "alternative_activity": alternative
                    }
                    alerts.append(alert_entry)

        # Update Shared State
        state["weather"]["alerts"] = alerts
        state["weather"]["raw_data"] = raw_weather_data
