import json
import os
from config import UTILITY_MODEL
from agents.gemini_helper import GeminiHelper

class FoodAgent:
    def __init__(self, gemini_key):
        self.gemini_key = gemini_key
        self.model = GeminiHelper(
            api_key=self.gemini_key,
            model_name=UTILITY_MODEL,
            system_instruction=(
                "Bạn là một Food Expert du lịch sành ăn ở miền Trung và Tây Nguyên Việt Nam. Nhiệm vụ của bạn là ghép nối "
                "lịch trình của du khách với các gợi ý quán ăn, nhà hàng đặc sản địa phương phù hợp nhất về vị trí địa lý "
                "và ngân sách ăn uống dự kiến. Trả về kết quả dạng JSON Array duy nhất."
            ),
        )

    def load_restaurants_data(self, destination):
        """Loads restaurant database and filters by destination."""
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "restaurants_data.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                all_restaurants = json.load(f)
            return all_restaurants.get(destination, [])
        except Exception as e:
            print(f"Error loading restaurants data: {e}")
            return []

    def run(self, state):
        """Recommends meals based on itinerary location, budget, and preference, then updates state."""
        request = state["user_request"]
        destination = request["destination"]
        budget_per_day = request["budget_per_day"]
        itinerary = state["itinerary"]

        # Load restaurants for destination
        restaurants = self.load_restaurants_data(destination)
        restaurants_str = json.dumps(restaurants, ensure_ascii=False, indent=2)

        # Estimate meal budget: say 30% of daily budget is for meals, split into 3 meals
        est_meal_budget = int((budget_per_day * 0.35) / 3)

        prompt = f"""
Hãy gợi ý quán ăn/nhà hàng phù hợp nhất cho từng buổi (Sáng, Chiều, Tối) của các ngày trong lịch trình dưới đây.

Lịch trình hiện tại của khách:
{json.dumps(itinerary, ensure_ascii=False, indent=2)}

Danh sách nhà hàng ẩm thực có sẵn:
{restaurants_str}

Ngân sách ước tính cho mỗi bữa ăn của một người: khoảng {est_meal_budget:,} VND.

Quy tắc ghép nối quán ăn:
1. **Theo Vị trí (Địa lý):** Gợi ý quán ăn ở gần hoặc cùng khu vực (region) với địa điểm tham quan trong buổi đó (ví dụ: buổi sáng đi Kỳ Co/Eo Gió ở Nhơn Lý -> ưu tiên gợi ý ăn hải sản ở Nhơn Lý. Buổi chiều đi Tháp Đôi ở trung tâm -> ăn bánh xèo/bún chả cá ở trung tâm).
2. **Theo Ngân sách:** 
   - So sánh mức giá trung bình (avg_price_person) của nhà hàng với ngân sách {est_meal_budget:,} VND.
   - Nếu ngân sách ăn uống quá thấp (ví dụ < 50,000 VND), chỉ gợi ý các quán ăn "Bình dân" giá rẻ hoặc quán ăn vỉa hè.
   - **CƠ CHẾ FALLBACK (Dự phòng):** Nếu không tìm thấy quán nào có giá phù hợp ngân sách trong khu vực đó, bạn phải bật cờ `"fallback_used": true` và gợi ý một phương án ăn uống bình dân chung trong khu vực (ví dụ: 'Tìm các quán bánh canh/bánh hỏi vỉa hè ở Nhơn Lý giá ~30k' hoặc 'Ghé chợ đêm Pleiku thưởng thức xiên nướng/bún mắm giá rẻ').
3. **Phân bổ bữa ăn:**
   - Sáng: Ăn sáng (bún chả cá, phở khô, bánh hỏi lòng heo).
   - Chiều (tầm trưa/chiều tối): Ăn trưa hoặc ăn xế (bánh xèo, hải sản, cơm nhà).
   - Tối: Ăn tối hoặc ăn vặt, cà phê ngắm phố (bò né, ốc trộn, lẩu, cháo sứa).

Bạn PHẢI trả về một JSON Array duy nhất chứa danh sách gợi ý quán ăn theo đúng định dạng sau:
[
  {{
    "day": 1,
    "session": "Sáng",
    "restaurant_name": "Tên quán hoặc mô tả phương án fallback",
    "specialty": "Tên món đặc sản của quán",
    "price_level": "Bình dân / Trung cấp / Cao cấp",
    "avg_price_person": 45000,
    "address": "Địa chỉ quán",
    "reason": "Giải thích ngắn gọn tại sao quán này phù hợp với địa điểm và ngân sách buổi sáng.",
    "fallback_used": false,
    "image_url": "URL hình ảnh của quán ăn/món ăn (nếu có trong danh sách)"
  }},
  ...
]
"""

        try:
            raw_output = self.model.generate_json(prompt)
            food_data = json.loads(raw_output)
            state["food_suggestions"]["meals"] = food_data
        except Exception as e:
            print("Failed to parse Food Agent output:", e)
            raise e
