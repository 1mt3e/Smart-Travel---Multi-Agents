import json
import os
from config import UTILITY_MODEL
from agents.gemini_helper import GeminiHelper

class LocalGuideAgent:
    def __init__(self, places_key=None, gemini_key=None):
        self.places_key = places_key
        self.gemini_key = gemini_key
        self.model = None
        if self.gemini_key:
            self.model = GeminiHelper(
                api_key=self.gemini_key,
                model_name=UTILITY_MODEL,
                system_instruction=(
                    "Bạn là một Hướng dẫn viên du lịch địa phương giàu kinh nghiệm (Local Guide). Nhiệm vụ của bạn là "
                    "cung cấp kiến thức sâu về lịch sử, lưu ý văn hóa, trang phục, và mẹo chụp ảnh cho các điểm đến trong "
                    "lịch trình của du khách. Trả về kết quả dạng JSON Array."
                ),
            )

    def load_guide_data(self, destination):
        """Loads local guide database from project files."""
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "local_guide_data.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                all_guide_data = json.load(f)
            return all_guide_data.get(destination, [])
        except Exception as e:
            print(f"Error loading local guide data: {e}")
            return []

    def mock_google_places_api(self, place_name):
        """Simulates Google Places API search for rating, reviews, and address."""
        # Simple simulation to demonstrate Google Places API tech stack integration
        import random
        ratings = {
            "Kỳ Co": {"rating": 4.6, "user_ratings_total": 12850, "address": "Nhơn Lý, Quy Nhơn, Bình Định"},
            "Eo Gió": {"rating": 4.6, "user_ratings_total": 15400, "address": "Bán đảo Phương Mai, Nhơn Lý, Quy Nhơn"},
            "Tháp Đôi": {"rating": 4.4, "user_ratings_total": 4500, "address": "Trần Hưng Đạo, Đống Đa, Quy Nhơn"},
            "Ghềnh Ráng Tiên Sa": {"rating": 4.5, "user_ratings_total": 8900, "address": "Ghềnh Ráng, Quy Nhơn"},
            "Hòn Khô": {"rating": 4.5, "user_ratings_total": 2300, "address": "Nhơn Hải, Quy Nhơn, Bình Định"},
            "Tượng Phật Chùa Ông Núi": {"rating": 4.7, "user_ratings_total": 3100, "address": "Cát Tiến, Phù Cát, Bình Định"},
            "Biển Hồ (Hồ T'Nưng)": {"rating": 4.6, "user_ratings_total": 9200, "address": "Pleiku, Gia Lai"},
            "Chùa Minh Thành": {"rating": 4.8, "user_ratings_total": 5600, "address": "232 Nguyễn Viết Xuân, Hội Phú, Pleiku"},
            "Núi lửa Chư Đăng Ya": {"rating": 4.6, "user_ratings_total": 1200, "address": "Chư Đăng Ya, Chư Păh, Gia Lai"},
            "Đồi chè Gia Lai & Hàng thông trăm tuổi": {"rating": 4.7, "user_ratings_total": 2400, "address": "Nghĩa Hưng, Chư Păh, Gia Lai"}
        }
        
        # Exact match check
        for key, val in ratings.items():
            if key.lower() in place_name.lower() or place_name.lower() in key.lower():
                return val
                
        # Fallback random generation
        return {
            "rating": round(random.uniform(4.2, 4.8), 1),
            "user_ratings_total": random.randint(500, 3000),
            "address": f"Khu du lịch sinh thái, {place_name}"
        }

    def run(self, state):
        """Processes places in itinerary, queries guide database & Google Places, calls Gemini, updates state."""
        request = state["user_request"]
        destination = request["destination"]
        itinerary = state["itinerary"]

        # Load local guide knowledge database
        guide_db = self.load_guide_data(destination)

        # Build list of places from itinerary
        places_to_guide = []
        for item in itinerary:
            for p in item.get("places", []):
                places_to_guide.append(p["name"])

        # Deduplicate places
        places_to_guide = list(set(places_to_guide))
        
        guide_tips_output = []
        
        # Gather info for all places
        places_context = []
        for name in places_to_guide:
            local_info = {}
            for db_item in guide_db:
                if db_item["place_name"].lower() in name.lower() or name.lower() in db_item["place_name"].lower():
                    local_info = db_item
                    break
            
            places_api_info = self.mock_google_places_api(name)
            places_context.append({
                "place": name,
                "local_info": local_info,
                "places_api_info": places_api_info
            })
            
        if self.model and places_to_guide:
            prompt = f"""
Hãy tạo các mẹo hướng dẫn viên địa phương hữu ích cho {len(places_to_guide)} điểm du lịch sau: {', '.join(places_to_guide)}.

Dưới đây là thông tin thô của từng địa điểm (từ Local Knowledge Base và Google Places API):
{json.dumps(places_context, ensure_ascii=False, indent=2)}

Hãy biên soạn lại thành một cẩm nang hướng dẫn ngắn gọn cho du khách. Đầu ra PHẢI là một mảng JSON Array chứa danh sách các đối tượng, mỗi đối tượng gồm các trường sau:
[
  {{
    "place": "Tên địa điểm",
    "history_context": "Bối cảnh lịch sử ngắn gọn trong 1-2 câu",
    "travel_tips": "Mẹo tham quan, góc chụp ảnh, trang phục khuyên dùng (2-3 câu ngắn gọn)",
    "rating": 4.5,
    "address": "Địa chỉ thực tế lấy từ Google Places"
  }}
]
Không thêm bất kỳ chữ nào ngoài JSON Array này.
"""
            try:
                raw_output = self.model.generate_json(prompt)
                tips_array = json.loads(raw_output)
                guide_tips_output = tips_array
            except Exception as e:
                print(f"Error generating guide tips with Gemini: {e}")
                # Fallback to local db for all places
                for ctx in places_context:
                    name = ctx["place"]
                    local_info = ctx["local_info"]
                    places_api_info = ctx["places_api_info"]
                    guide_tips_output.append({
                        "place": name,
                        "history_context": local_info.get("history_context", f"Địa danh nổi tiếng tại {destination}."),
                        "travel_tips": f"Trang phục: {local_info.get('dress_code', 'Tự do')}. Mẹo chụp ảnh: {local_info.get('best_photo_spot', 'Cảnh quan xung quanh')}.",
                        "rating": places_api_info["rating"],
                        "address": places_api_info["address"]
                    })
        else:
            # No Gemini key fallback
            for ctx in places_context:
                name = ctx["place"]
                local_info = ctx["local_info"]
                places_api_info = ctx["places_api_info"]
                guide_tips_output.append({
                    "place": name,
                    "history_context": local_info.get("history_context", f"Địa danh nổi tiếng tại {destination}."),
                    "travel_tips": f"Mẹo: {local_info.get('travel_tips', 'Tham quan tự do')}. Trang phục: {local_info.get('dress_code', 'Tự do')}.",
                    "rating": places_api_info["rating"],
                    "address": places_api_info["address"]
                })

        # Save to Shared State
        state["local_guide_tips"] = guide_tips_output
