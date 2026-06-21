import json
import os
from config import UTILITY_MODEL
from agents.gemini_helper import GeminiHelper

class ReplanAgent:
    """
    Re-plan Agent: Tự động tạo lịch trình thay thế khi:
    1. Thời tiết xấu (mưa lớn ≥ 60% tại nhiều địa điểm)
    2. Tổng chi phí vượt budget
    """

    def __init__(self, gemini_key):
        self.gemini_key = gemini_key
        self.model = GeminiHelper(
            api_key=self.gemini_key,
            model_name=UTILITY_MODEL,
            system_instruction=(
                "Bạn là một Travel Re-planner thông minh chuyên về du lịch Quy Nhơn, Bình Định. "
                "Khi lịch trình gặp sự cố (mưa, vượt ngân sách), bạn tạo ra phương án thay thế "
                "sáng tạo, thực tế và vẫn thú vị cho du khách. "
                "Ưu tiên các hoạt động trong nhà (indoor), trải nghiệm văn hóa, ẩm thực địa phương. "
                "Trả về JSON hợp lệ."
            ),
        )

    def check_rain_trigger(self, state):
        """Check if rain alerts warrant a re-plan."""
        alerts = state.get("weather", {}).get("alerts", [])
        high_rain_count = sum(1 for a in alerts if a.get("alert", False))
        total_sessions = len(state.get("itinerary", []))
        # Trigger if >40% of sessions have rain warnings
        return high_rain_count > 0 and (high_rain_count / max(total_sessions, 1)) >= 0.40

    def check_budget_trigger(self, state):
        """Check if estimated costs exceed budget."""
        request = state.get("user_request", {})
        budget_per_day = request.get("budget_per_day", 2000000)
        days = request.get("days", 3)
        total_budget = budget_per_day * days

        # Estimate total cost
        hotel = state.get("booking", {}).get("hotel", {})
        hotel_cost = hotel.get("price_per_night", 0) * days

        meals = state.get("food_suggestions", {}).get("meals", [])
        avg_meal = sum(m.get("avg_price_person", 0) for m in meals) / max(len(meals), 1)
        food_cost = avg_meal * 3 * days  # 3 meals/day

        places = [p for item in state.get("itinerary", []) for p in item.get("places", [])]
        ticket_cost = sum(p.get("price", 0) for p in places)

        estimated_total = hotel_cost + food_cost + ticket_cost
        return estimated_total > total_budget * 1.3  # 30% over budget triggers replan

    def create_rain_replan(self, state):
        """Generate indoor alternative itinerary for rainy days."""
        request = state["user_request"]
        destination = request["destination"]
        days = request["days"]
        budget_per_day = request["budget_per_day"]
        alerts = state.get("weather", {}).get("alerts", [])

        rainy_sessions = [
            f"Ngày {a['day']} buổi {a['session']}: {a['place']}"
            for a in alerts if a.get("alert")
        ]
        rainy_str = "\n".join(rainy_sessions)

        indoor_places = self._load_indoor_alternatives()

        prompt = f"""
Lịch trình du lịch {days} ngày tại {destination} đang gặp thời tiết xấu tại các buổi sau:
{rainy_str}

Hãy tạo phương án thay thế (re-plan) cho những buổi bị mưa đó với các hoạt động trong nhà (indoor) 
hoặc có mái che tại Quy Nhơn, thú vị và phù hợp ngân sách {budget_per_day:,} VND/ngày.

Các hoạt động trong nhà gợi ý tại Quy Nhơn:
{json.dumps(indoor_places, ensure_ascii=False, indent=2)}

Hãy tạo ra {len(alerts)} lịch trình thay thế, mỗi cái cho một buổi bị mưa, theo format JSON:
[
  {{
    "original_day": 1,
    "original_session": "Sáng",
    "original_place": "Tên địa điểm bị mưa",
    "replan_activity": "Tên hoạt động thay thế",
    "replan_location": "Địa điểm cụ thể",
    "replan_description": "Mô tả hoạt động thay thế 2-3 câu, vui vẻ và hấp dẫn cho GenZ",
    "replan_cost_estimate": "Ước tính chi phí (VND)",
    "address": "Địa chỉ",
    "rain_tip": "Mẹo vui khi đi trong mưa"
  }}
]
"""
        try:
            raw_output = self.model.generate_json(prompt)
            return json.loads(raw_output)
        except Exception as e:
            print(f"ReplanAgent rain error: {e}")
            return self._fallback_rain_replan(alerts)

    def create_budget_replan(self, state):
        """Generate budget-saving alternatives."""
        request = state["user_request"]
        budget_per_day = request["budget_per_day"]
        destination = request["destination"]

        hotel = state.get("booking", {}).get("hotel", {})
        meals = state.get("food_suggestions", {}).get("meals", [])

        prompt = f"""
Du khách đến {destination} với ngân sách {budget_per_day:,} VND/ngày nhưng chi phí hiện tại vượt quá budget.

Khách sạn hiện tại: {hotel.get("name", "N/A")} - {hotel.get("price_per_night", 0):,} VND/đêm

Hãy đề xuất phương án tiết kiệm hơn theo format JSON:
{{
  "hotel_suggestion": {{
    "name": "Tên homestay/khách sạn rẻ hơn tại Quy Nhơn",
    "price_per_night": 300000,
    "address": "Địa chỉ",
    "description": "Tại sao chọn nơi này"
  }},
  "food_savings": [
    {{
      "session": "Sáng",
      "suggestion": "Quán bình dân nào đó",
      "price": 35000,
      "tip": "Mẹo tiết kiệm"
    }}
  ],
  "activity_savings": [
    {{
      "suggestion": "Hoạt động miễn phí hoặc rẻ",
      "price": 0,
      "description": "Mô tả"
    }}
  ],
  "total_savings_estimate": "Tiết kiệm ước tính mỗi ngày",
  "summary": "Tóm tắt kế hoạch tiết kiệm 2-3 câu"
}}
"""
        try:
            raw_output = self.model.generate_json(prompt)
            return json.loads(raw_output)
        except Exception as e:
            print(f"ReplanAgent budget error: {e}")
            return self._fallback_budget_replan(budget_per_day)

    def run(self, state):
        """Main entry point - checks triggers and adds replan data to state."""
        state["replan"] = {
            "rain_triggered": False,
            "budget_triggered": False,
            "rain_alternatives": [],
            "budget_alternatives": None
        }

        # Check rain
        if self.check_rain_trigger(state):
            state["replan"]["rain_triggered"] = True
            state["replan"]["rain_alternatives"] = self.create_rain_replan(state)

        # Check budget
        if self.check_budget_trigger(state):
            state["replan"]["budget_triggered"] = True
            state["replan"]["budget_alternatives"] = self.create_budget_replan(state)

    def _load_indoor_alternatives(self):
        """Return curated list of indoor activities in Quy Nhon."""
        return [
            {"name": "Bảo tàng Bình Định", "type": "indoor", "price": 20000,
             "description": "Khám phá văn hóa Chăm Pa và lịch sử Bình Định"},
            {"name": "Nhà lưu niệm Hàn Mặc Tử", "type": "indoor", "price": 10000,
             "description": "Tìm hiểu cuộc đời nhà thơ huyền thoại"},
            {"name": "Workshop nấu ăn đặc sản Quy Nhơn", "type": "indoor", "price": 200000,
             "description": "Học nấu bánh xèo tôm nhảy, chả ram tôm đất"},
            {"name": "Massage truyền thống & Spa", "type": "indoor", "price": 200000,
             "description": "Thư giãn với massage Việt Nam truyền thống"},
            {"name": "Mua sắm Trung tâm thương mại Quy Nhơn", "type": "indoor", "price": 0,
             "description": "Mua sắm và khám phá ẩm thực trong trung tâm thương mại"},
            {"name": "Café & làm việc tại Café Đông Dương", "type": "indoor", "price": 30000,
             "description": "Thưởng thức cà phê phin trong không gian vintage đẹp"},
            {"name": "Tham quan Thành Hoàng Đế (mái che)", "type": "outdoor_covered", "price": 30000,
             "description": "Di tích lịch sử thời Tây Sơn, có thể đi khi mưa nhẹ"}
        ]

    def _fallback_rain_replan(self, alerts):
        """Simple fallback when LLM fails."""
        alternatives = []
        indoor_options = [
            ("Bảo tàng Bình Định", "Đường Nguyễn Thái Học", "Khám phá lịch sử và văn hóa Chăm Pa", "20,000 VND"),
            ("Café Đông Dương", "109 Trần Cao Vân", "Thưởng thức cà phê phin vintage khi trời mưa", "30,000-50,000 VND"),
            ("Workshop nấu ăn", "Trung tâm dạy nấu ăn Quy Nhơn", "Học nấu đặc sản Quy Nhơn trong nhà", "200,000 VND")
        ]
        for i, alert in enumerate(alerts):
            opt = indoor_options[i % len(indoor_options)]
            alternatives.append({
                "original_day": alert["day"],
                "original_session": alert["session"],
                "original_place": alert["place"],
                "replan_activity": opt[0],
                "replan_location": opt[1],
                "replan_description": opt[2],
                "replan_cost_estimate": opt[3],
                "address": opt[1],
                "rain_tip": "Mang áo mưa hoặc ô, đồ ăn vặt để thưởng thức trong không gian ấm cúng!"
            })
        return alternatives

    def _fallback_budget_replan(self, budget_per_day):
        """Simple budget fallback."""
        return {
            "hotel_suggestion": {
                "name": "BB Hostel Quy Nhơn",
                "price_per_night": 150000,
                "address": "23 Tây Sơn, TP. Quy Nhơn",
                "description": "Hostel sạch sẽ, trung tâm, tiết kiệm nhất Quy Nhơn"
            },
            "food_savings": [
                {"session": "Sáng", "suggestion": "Bún chả cá vỉa hè", "price": 30000, "tip": "Ăn sáng vỉa hè ngon và rẻ"},
                {"session": "Trưa", "suggestion": "Cơm đĩa bình dân", "price": 40000, "tip": "Quán cơm gần chợ luôn rẻ và ngon"},
                {"session": "Tối", "suggestion": "Chợ đêm Quy Nhơn", "price": 50000, "tip": "Ăn vặt ở chợ đêm tiết kiệm hơn nhà hàng"}
            ],
            "activity_savings": [
                {"suggestion": "Đi bộ bãi biển Quy Nhơn", "price": 0, "description": "Miễn phí, đẹp như resort"},
                {"suggestion": "Cầu Thị Nại ngắm hoàng hôn", "price": 0, "description": "Miễn phí, view đỉnh cao"}
            ],
            "total_savings_estimate": f"~{budget_per_day // 2:,} VND/ngày",
            "summary": "Tập trung vào các địa điểm miễn phí, ăn bình dân và ở hostel để tiết kiệm tối đa."
        }
