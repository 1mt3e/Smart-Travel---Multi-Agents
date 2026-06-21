import json
import os
from config import UTILITY_MODEL
from agents.gemini_helper import GeminiHelper

class BookingAgent:
    def __init__(self, gemini_key):
        self.gemini_key = gemini_key
        self.model = GeminiHelper(
            api_key=self.gemini_key,
            model_name=UTILITY_MODEL,
            system_instruction=(
                "Bạn là một chuyên viên đặt phòng và dịch vụ du lịch (Booking Agent). Nhiệm vụ của bạn là dựa vào "
                "ngân sách và sở thích khách hàng để đề xuất khách sạn/homestay và phương tiện di chuyển phù hợp nhất. "
                "Trả về kết quả chính xác dạng JSON duy nhất."
            ),
        )

    def load_booking_data(self, destination):
        """Loads booking data database."""
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "booking_data.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                all_booking_data = json.load(f)
            return all_booking_data.get(destination, {"accommodations": [], "transports": []})
        except Exception as e:
            print(f"Error loading booking data: {e}")
            return {"accommodations": [], "transports": []}

    def run(self, state):
        """Reads request, matches accommodation and transport based on budget, calls Gemini, updates state."""
        request = state["user_request"]
        destination = request["destination"]
        budget_per_day = request["budget_per_day"]
        has_kids = request["has_kids"]
        days = request["days"]

        # Load database
        db_data = self.load_booking_data(destination)
        accommodations_str = json.dumps(db_data["accommodations"], ensure_ascii=False, indent=2)
        transports_str = json.dumps(db_data["transports"], ensure_ascii=False, indent=2)

        # Classify budget level
        if budget_per_day < 600000:
            user_level = "Bình dân"
        elif budget_per_day <= 1800000:
            user_level = "Trung cấp"
        else:
            user_level = "Cao cấp"

        prompt = f"""
Hãy chọn một Khách sạn/Homestay và một Phương tiện di chuyển phù hợp nhất cho chuyến đi {days} ngày tại {destination}.

Yêu cầu đầu vào:
- Mức ngân sách phân loại: {user_level} (ngân sách chi tiêu mỗi ngày: {budget_per_day:,} VND).
- Có trẻ em đi cùng? { 'Có trẻ nhỏ (hãy ưu tiên các khách sạn tiện nghi có hồ bơi/khuôn viên, phương tiện di chuyển an toàn như taxi/ô tô).' if has_kids else 'Không có trẻ nhỏ (có thể chọn xe máy di chuyển năng động và homestay trải nghiệm).' }

Danh sách nơi lưu trú có sẵn:
{accommodations_str}

Danh sách phương tiện di chuyển có sẵn:
{transports_str}

Quy tắc lựa chọn:
1. **Lưu trú:** 
   - Giá phòng mỗi đêm (price_per_night) lý tưởng nên nằm trong khoảng 30-40% ngân sách ngày {budget_per_day:,} VND.
   - **FALLBACK (Dự phòng):** Nếu ngân sách của khách quá thấp không thuê nổi phòng nào theo mức ngân sách đó, bạn phải tự động chọn phòng rẻ nhất có sẵn trong cơ sở dữ liệu và đặt cờ `"fallback_used": true` trong kết quả khách sạn.
2. **Phương tiện di chuyển:** Chọn phương tiện phù hợp nhất với nhóm khách (trẻ nhỏ -> Taxi/ô tô; thanh niên, ngân sách thấp -> xe máy).

Bạn PHẢI trả về một JSON duy nhất chứa đúng thông tin đề xuất theo cấu trúc mẫu sau:
{{
  "hotel": {{
    "name": "Tên khách sạn được chọn",
    "type": "Loại hình (ví dụ: Khách sạn 4 sao)",
    "price_per_night": 1100000,
    "rating": 4.7,
    "address": "Địa chỉ khách sạn",
    "description": "Giải thích ngắn gọn tại sao chọn khách sạn này phù hợp với gia đình/ngân sách của khách.",
    "fallback_used": false,
    "image_url": "URL hình ảnh của khách sạn (nếu có trong danh sách)"
  }},
  "transport": {{
    "type": "Thuê xe máy / Taxi / Ô tô tự lái",
    "price_estimate": "Mức giá ước tính từ dữ liệu",
    "provider_info": "Thông tin liên hệ/tên nhà cung cấp từ dữ liệu",
    "description": "Giải thích tại sao lựa chọn phương tiện này phù hợp với chuyến đi."
  }}
}}
Không thêm bất kỳ chữ nào ngoài JSON Object này.
"""

        try:
            raw_output = self.model.generate_json(prompt)
            booking_res = json.loads(raw_output)
            state["booking"] = booking_res
        except Exception as e:
            print("Failed to parse Booking Agent output:", e)
            # Hardcoded fallback if LLM call fails
            accomm_fallback = db_data["accommodations"][-1] if db_data["accommodations"] else {}
            trans_fallback = db_data["transports"][0] if db_data["transports"] else {}
            state["booking"] = {
                "hotel": {
                    "name": accomm_fallback.get("name", "Nhà nghỉ địa phương"),
                    "type": accomm_fallback.get("type", "Bình dân"),
                    "price_per_night": accomm_fallback.get("price_per_night", 250000),
                    "rating": accomm_fallback.get("rating", 4.0),
                    "address": accomm_fallback.get("address", "Trung tâm thành phố"),
                    "description": "Fallback được kích hoạt do lỗi hệ thống.",
                    "fallback_used": True,
                    "image_url": accomm_fallback.get("image_url", "")
                },
                "transport": {
                    "type": trans_fallback.get("type", "Thuê xe máy"),
                    "price_estimate": trans_fallback.get("price_estimate", "120,000 VND/ngày"),
                    "provider_info": trans_fallback.get("provider_info", "Dịch vụ địa phương"),
                    "description": "Phương tiện di chuyển mặc định tiết kiệm."
                }
            }
