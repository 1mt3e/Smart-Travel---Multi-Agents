import threading
import time
from datetime import datetime

# Import individual agents
from agents.itinerary_agent import ItineraryAgent
from agents.weather_agent import WeatherAgent
from agents.food_agent import FoodAgent
from agents.local_guide_agent import LocalGuideAgent
from agents.booking_agent import BookingAgent
from agents.translate_agent import TranslateAgent
from agents.replan_agent import ReplanAgent

class Orchestrator:
    def __init__(self, gemini_key, weather_key=None):
        self.gemini_key = gemini_key
        self.weather_key = weather_key
        self.state = {"agent_logs": []}

    def log_agent_action(self, agent_name, action):
        """Helper to append log entries with timestamp to the Shared State."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            "agent": agent_name,
            "action": action,
            "timestamp": timestamp
        }
        self.state["agent_logs"].append(log_entry)
        try:
            print(f"[{timestamp}] {agent_name}: {action}")
        except UnicodeEncodeError:
            safe_action = action.encode("ascii", errors="replace").decode("ascii")
            print(f"[{timestamp}] {agent_name}: {safe_action}")
            
        if hasattr(self, "on_state_update") and self.on_state_update:
            self.on_state_update(log_entry)

    def run(self, destination, days, budget_per_day, language, has_kids, preferences="", weather_sim_mode="Nắng đẹp", on_state_update=None):
        """Runs the entire multi-agent pipeline using a shared state object."""
        self.on_state_update = on_state_update
        
        import os
        import json
        
        # Check cache for Hackathon Demo Mode
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
        os.makedirs(cache_dir, exist_ok=True)
        import re
        safe_dest = re.sub(r'[\\/:"<>|]', '', destination).strip().replace(' ', '_')
        cache_file = os.path.join(cache_dir, f"{safe_dest}_{days}_{budget_per_day}.json")
        
        if os.path.exists(cache_file):
            self.log_agent_action("Orchestrator", "Phát hiện bản lưu tạm (Cache). Kích hoạt chế độ siêu tốc!")
            time.sleep(0.5)
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_state = json.load(f)
            
            # Simulate logs
            self.log_agent_action("Itinerary Agent", "Tải khung lịch trình từ bộ nhớ...")
            time.sleep(0.5)
            self.log_agent_action("Weather Agent", "Đồng bộ dữ liệu thời tiết...")
            self.log_agent_action("Food Agent", "Đồng bộ gợi ý ẩm thực...")
            time.sleep(0.5)
            self.log_agent_action("Local Guide Agent", "Đồng bộ cẩm nang địa phương...")
            self.log_agent_action("Booking Agent", "Đồng bộ phòng và xe...")
            time.sleep(0.5)
            self.log_agent_action("Re-plan Agent", "Kiểm tra thời tiết & ngân sách...")
            self.log_agent_action("Translate Agent", "Hoàn tất biên dịch.")
            self.log_agent_action("Orchestrator", "Toàn bộ luồng kết thúc thành công!")
            time.sleep(0.5)
            
            self.state = cached_state
            return self.state
        
        # 1. Initialize Shared State
        self.state = {
            "user_request": {
                "destination": destination,
                "days": int(days),
                "budget_per_day": int(budget_per_day),
                "language": language,
                "has_kids": bool(has_kids),
                "preferences": preferences,
                "weather_sim_mode": weather_sim_mode
            },
            "itinerary": [],
            "weather": {
                "alerts": [],
                "raw_data": {}
            },
            "food_suggestions": {
                "meals": []
            },
            "booking": {},
            "local_guide_tips": [],
            "replan": {
                "rain_triggered": False,
                "budget_triggered": False,
                "rain_alternatives": [],
                "budget_alternatives": None
            },
            "final_translated": None,
            "agent_logs": []
        }
        
        self.log_agent_action("Orchestrator", "Khởi tạo Shared State thành công.")

        # 2. Run Itinerary Agent (Creates base schedule)
        self.log_agent_action("Orchestrator", "Kích hoạt Itinerary Agent dựng khung lịch trình...")
        itinerary_agent = ItineraryAgent(self.gemini_key)
        try:
            itinerary_agent.run(self.state)
            self.log_agent_action("Itinerary Agent", f"Hoàn thành tạo khung lịch trình ({len(self.state['itinerary'])} ngày).")
        except Exception as e:
            self.log_agent_action("Itinerary Agent", f"LỖI: {str(e)}")
            # Critical fallback: Create an empty itinerary outline so subsequent agents don't crash
            self.state["itinerary"] = [
                {"day": i+1, "session": session, "places": []} 
                for i in range(days) 
                for session in ["Sáng", "Chiều", "Tối"]
            ]
            self.log_agent_action("Orchestrator", "Kích hoạt fallback: Tạo khung lịch trình rỗng.")
            
        time.sleep(0.5)

        # 3. Run Weather, Food, Local Guide and Booking Agents in PARALLEL
        self.log_agent_action("Orchestrator", "Kích hoạt 4 Agents (Weather, Food, Guide, Booking) chạy song song...")
        
        weather_agent = WeatherAgent(self.weather_key, self.gemini_key)
        food_agent = FoodAgent(self.gemini_key)
        guide_agent = LocalGuideAgent(places_key=None, gemini_key=self.gemini_key)
        booking_agent = BookingAgent(self.gemini_key)

        def run_weather():
            try:
                self.log_agent_action("Weather Agent", "Bắt đầu phân tích thời tiết cho lịch trình...")
                weather_agent.run(self.state)
                self.log_agent_action("Weather Agent", "Hoàn thành phân tích thời tiết và tích hợp cảnh báo.")
            except Exception as e:
                self.log_agent_action("Weather Agent", f"LỖI: {str(e)}")
                self.state["weather"] = {
                    "alerts": [{"warning": "Chưa có dữ liệu thời tiết thực tế, vui lòng tự kiểm tra trước khi đi."}],
                    "raw_data": {}
                }
                self.log_agent_action("Weather Agent", "Kích hoạt fallback: Ghi chú khuyến nghị thời tiết.")

        def run_food():
            try:
                self.log_agent_action("Food Agent", "Bắt đầu tìm kiếm gợi ý ẩm thực theo ngân sách...")
                food_agent.run(self.state)
                self.log_agent_action("Food Agent", f"Hoàn thành gợi ý ăn uống ({len(self.state['food_suggestions']['meals'])} bữa).")
            except Exception as e:
                self.log_agent_action("Food Agent", f"LỖI: {str(e)}")
                self.state["food_suggestions"] = {
                    "meals": [],
                    "general_note": "Không thể tải gợi ý quán ăn chi tiết. Hãy thử ẩm thực tại chợ đêm."
                }
                self.log_agent_action("Food Agent", "Kích hoạt fallback: Gợi ý chung khu ẩm thực.")

        def run_guide():
            try:
                self.log_agent_action("Local Guide Agent", "Bắt đầu thu thập bối cảnh di sản và mẹo du lịch địa phương...")
                guide_agent.run(self.state)
                self.log_agent_action("Local Guide Agent", f"Hoàn thành thu thập cẩm nang ({len(self.state['local_guide_tips'])} địa điểm).")
            except Exception as e:
                self.log_agent_action("Local Guide Agent", f"LỖI: {str(e)}")
                self.state["local_guide_tips"] = []
                self.log_agent_action("Local Guide Agent", "Kích hoạt fallback: Bỏ qua thông tin cẩm nang địa phương.")

        def run_booking():
            try:
                self.log_agent_action("Booking Agent", "Bắt đầu phân tích ngân sách để tìm phòng và xe...")
                booking_agent.run(self.state)
                self.log_agent_action("Booking Agent", "Hoàn thành đề xuất khách sạn và phương tiện di chuyển.")
            except Exception as e:
                self.log_agent_action("Booking Agent", f"LỖI: {str(e)}")
                self.state["booking"] = {
                    "hotel": {"name": "Nhà nghỉ bình dân địa phương", "price_per_night": 250000, "fallback_used": True},
                    "transport": {"type": "Thuê xe máy", "price_estimate": "120,000 VND/ngày"}
                }
                self.log_agent_action("Booking Agent", "Kích hoạt fallback: Đề xuất dịch vụ mặc định.")

        # Start threads with a slight stagger to avoid instant 429 Rate Limits
        thread_weather = threading.Thread(target=run_weather)
        thread_food = threading.Thread(target=run_food)
        thread_guide = threading.Thread(target=run_guide)
        thread_booking = threading.Thread(target=run_booking)

        thread_weather.start()
        time.sleep(0.5)
        thread_food.start()
        time.sleep(0.5)
        thread_guide.start()
        time.sleep(0.5)
        thread_booking.start()

        # Wait for all threads to finish
        thread_weather.join()
        thread_food.join()
        thread_guide.join()
        thread_booking.join()

        self.log_agent_action("Orchestrator", "Hoàn thành xử lý song song từ cả 4 Agents.")
        time.sleep(0.5)

        # 4. Run Re-plan Agent
        self.log_agent_action("Orchestrator", "Kích hoạt Re-plan Agent kiểm tra thời tiết & ngân sách...")
        replan_agent = ReplanAgent(self.gemini_key)
        try:
            replan_agent.run(self.state)
            rain_status = "cần re-plan mưa" if self.state["replan"]["rain_triggered"] else "thời tiết ổn"
            budget_status = "vượt budget" if self.state["replan"]["budget_triggered"] else "trong ngân sách"
            self.log_agent_action("Re-plan Agent", f"Hoàn thành phân tích: {rain_status}, {budget_status}.")
        except Exception as e:
            self.log_agent_action("Re-plan Agent", f"LỖI: {str(e)}")

        # 5. Run Translate Agent (Last step)
        self.log_agent_action("Orchestrator", f"Kích hoạt Translate Agent dịch sang ngôn ngữ: {language}...")
        translate_agent = TranslateAgent(self.gemini_key)
        try:
            translate_agent.run(self.state)
            self.log_agent_action("Translate Agent", "Hoàn thành dịch thuật toàn bộ kế hoạch chuyến đi.")
        except Exception as e:
            self.log_agent_action("Translate Agent", f"LỖI: {str(e)}")
            self.state["final_translated"] = {
                "translated_itinerary": "Translation failed. Original content used.",
                "useful_phrases": []
            }
            self.log_agent_action("Translate Agent", "Kích hoạt fallback: Sử dụng bản gốc tiếng Việt.")

        self.log_agent_action("Orchestrator", "Toàn bộ luồng Multi-agent kết thúc thành công!")

        # Save to cache only if itinerary actually has places
        has_places = any(len(session.get("places", [])) > 0 for session in self.state.get("itinerary", []))
        if has_places:
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(self.state, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print("Failed to save cache:", e)

        return self.state
