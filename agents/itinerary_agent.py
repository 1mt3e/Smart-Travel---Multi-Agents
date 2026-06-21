import json
import os
from config import ITINERARY_MODEL
from agents.gemini_helper import GeminiHelper

class ItineraryAgent:
    def __init__(self, gemini_key):
        self.gemini_key = gemini_key
        self.model = GeminiHelper(
            api_key=self.gemini_key,
            model_name=ITINERARY_MODEL,
            system_instruction=(
                "Bạn là một chuyên gia lập kế hoạch du lịch chuyên nghiệp của Việt Nam. Nhiệm vụ của bạn là lập một "
                "khung lịch trình chi tiết và hợp lý cho chuyến đi dựa trên danh sách các địa điểm có sẵn ở Quy Nhơn hoặc Gia Lai. "
                "Hãy trả về kết quả dưới dạng JSON hợp lệ tuân thủ chính xác cấu trúc được yêu cầu. Không thêm bất kỳ văn bản giải thích "
                "nào ngoài JSON."
            ),
        )

    def load_places_data(self, destination):
        """Loads places database and filters by destination."""
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "places_data.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                all_places = json.load(f)
            return all_places.get(destination, [])
        except Exception as e:
            print(f"Error loading places data: {e}")
            return []

    def run(self, state):
        """Reads user_request from state, plans itinerary using Gemini, and saves it to state."""
        request = state["user_request"]
        destination = request["destination"]
        days = request["days"]
        has_kids = request["has_kids"]
        preferences = request["preferences"]
        budget_per_day = request["budget_per_day"]

        # Load list of available places
        places = self.load_places_data(destination)
        places_str = json.dumps(places, ensure_ascii=False, indent=2)

        prompt = f"""
Hãy thiết lập một lịch trình chi tiết cho chuyến đi {days} ngày đến {destination} bằng cách chọn các địa danh phù hợp nhất từ danh sách địa điểm dưới đây.

Yêu cầu cụ thể:
1. **Lịch trình tối ưu địa lý:** Sắp xếp các điểm tham quan gần nhau trong cùng một ngày hoặc cùng một buổi (Sáng, Chiều, Tối) để tránh việc di chuyển ngược đường mất nhiều thời gian.
2. **Hợp lý về thời gian:** Mỗi buổi chỉ nên xếp 1 - 2 địa điểm tùy theo thời gian tham quan trung bình (avg_duration) của điểm đó.
3. **Phù hợp với nhóm khách:** 
   - Có trẻ nhỏ đi cùng? { 'Có trẻ nhỏ (hãy chọn các điểm nhẹ nhàng, an toàn, có bãi bằng phẳng, khu vui chơi, tránh di chuyển thuyền sóng lớn hoặc leo bậc thang dài).' if has_kids else 'Không có trẻ nhỏ (có thể thoải mái di chuyển, leo núi hoặc đi cano đảo).' }
   - Ngân sách mỗi ngày: {budget_per_day:,} VND/ngày (hãy chú ý giá vé vào cửa 'price' để tổng tiền vé không vượt quá ngân sách).
   - Sở thích cá nhân: {preferences}
4. **Phân chia buổi:** Chia rõ lịch trình mỗi ngày thành 3 buổi: Sáng, Chiều, Tối. 
   - Sáng: Điểm tham quan ngoài trời, năng động.
   - Chiều: Điểm check-in nhẹ nhàng hoặc bãi biển, đồi cát ngắm hoàng hôn.
   - Tối: Gợi ý đi dạo phố, ngắm quảng trường, cầu Thị Nại hoặc đi bộ chợ đêm.

Danh sách các địa điểm có sẵn:
{places_str}

Bạn PHẢI trả về một JSON Array duy nhất chứa lịch trình theo mẫu cấu trúc dưới đây. Mỗi phần tử trong mảng đại diện cho một buổi (session) của một ngày cụ thể (Sáng/Chiều/Tối):
[
  {{
    "day": 1,
    "session": "Sáng",
    "places": [
      {{
        "name": "Tên địa điểm từ danh sách (chính xác)",
        "coordinate": {{"lat": 13.9248, "lon": 109.2872}},
        "avg_duration": "1.5h",
        "description": "Mô tả ngắn gọn hoạt động tại đây và lý do chọn điểm này phù hợp với yêu cầu của user.",
        "image_url": "URL hình ảnh của địa điểm (nếu có trong danh sách)"
      }}
    ]
  }},
  {{
    "day": 1,
    "session": "Chiều",
    "places": [...]
  }},
  {{
    "day": 1,
    "session": "Tối",
    "places": [] 
  }}
]
*Lưu ý: Với buổi Tối, nếu không có điểm tham quan cố định trong danh sách, hãy gợi ý đi dạo khu phố/khu vực trung tâm (ví dụ: Chợ đêm Quy Nhơn, Quảng trường Đại Đoàn Kết Gia Lai) và điền tên địa điểm cùng tọa độ vùng trung tâm tương ứng.
"""

        try:
            raw_output = self.model.generate_json(prompt)
            itinerary_data = json.loads(raw_output)
            state["itinerary"] = itinerary_data
        except Exception as e:
            print("Failed to parse Itinerary Agent output:", e)
            raise e
