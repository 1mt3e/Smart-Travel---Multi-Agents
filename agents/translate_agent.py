import json
from config import UTILITY_MODEL
from agents.gemini_helper import GeminiHelper

class TranslateAgent:
    def __init__(self, gemini_key):
        self.gemini_key = gemini_key
        self.model = GeminiHelper(
            api_key=self.gemini_key,
            model_name=UTILITY_MODEL,
            system_instruction=(
                "Bạn là một biên dịch viên du lịch chuyên nghiệp và hướng dẫn viên bản địa. Nhiệm vụ của bạn là tổng hợp "
                "toàn bộ thông tin lịch trình, thời tiết, quán ăn, khách sạn, xe cộ, và mẹo hướng dẫn viên địa phương từ Shared State, "
                "dịch sang ngôn ngữ đích được yêu cầu, và định dạng thành một văn bản Markdown hoàn hảo."
            ),
        )

    def run(self, state):
        """Translates the compiled itinerary, booking, and guide tips, updating the state."""
        request = state["user_request"]
        language = request["language"]
        
        # Compile a simplified representation of the state for the LLM to translate/format
        data_to_translate = {
            "destination": request["destination"],
            "days": request["days"],
            "preferences": request["preferences"],
            "has_kids": request["has_kids"],
            "itinerary": state["itinerary"],
            "weather_alerts": state["weather"]["alerts"],
            "weather_raw": state["weather"]["raw_data"],
            "food_suggestions": state["food_suggestions"]["meals"],
            "booking": state.get("booking", {}),
            "local_guide_tips": state.get("local_guide_tips", [])
        }

        prompt = f"""
Hãy dịch toàn bộ thông tin lịch trình du lịch tổng hợp dưới đây sang ngôn ngữ đích: **{language}**.

Dữ liệu lịch trình thô cần tổng hợp và dịch:
{json.dumps(data_to_translate, ensure_ascii=False, indent=2)}

Yêu cầu đầu ra:
1. **translated_itinerary (Lịch trình đã dịch):** 
   - Trả về dưới dạng một MẢNG (Array) các đối tượng JSON, mỗi đối tượng đại diện cho một Ngày.
   - Cấu trúc của mỗi đối tượng Ngày:
     - "day_title": Tiêu đề của ngày bằng ngôn ngữ {language} (Ví dụ: "Ngày 1: Khám phá vẻ đẹp hoang sơ")
     - "content": Nội dung chi tiết của ngày đó bằng {language} (viết bằng Markdown). BẮT BUỘC trình bày RẤT NGẮN GỌN nhưng đầy đủ thông tin: Sáng/Chiều/Tối đi đâu, thời tiết ra sao, quán ăn nào và mẹo địa phương. ĐẶC BIỆT: BẮT BUỘC phải chèn hình ảnh của địa điểm hoặc món ăn vào Markdown bằng cú pháp `![Tên](image_url)` nếu có `image_url` trong dữ liệu thô truyền vào.
     - ĐẶC BIỆT CHÚ Ý: Bắt buộc phải TỰ ƯỚC TÍNH "Giá vé tham quan" cho các địa điểm tham quan (dựa trên kiến thức thực tế của bạn) và ghi rõ vào trong phần "content".

2. **useful_phrases (Mẫu câu giao tiếp):**
   - Tạo ra danh sách 4-5 câu giao tiếp tiếng Việt cơ bản và cực kỳ thiết thực cho du khách khi đi {request['destination']} (ví dụ: Chào hỏi, hỏi giá tiền, nhờ tính tiền, yêu cầu không ăn cay).
   - Mỗi câu cần có:
     - "vietnamese": câu tiếng Việt chính xác.
     - "translated": bản dịch câu đó sang ngôn ngữ **{language}**.
     - "pronunciation": phiên âm cách đọc tiếng Việt giúp khách nước ngoài dễ phát âm (ví dụ: "Cảm ơn" -> "Cam uhn").

Bạn PHẢI trả về một JSON Object chứa đúng 2 trường dưới đây:
{{
  "translated_itinerary": [
    {{
      "day_title": "Ngày 1: Tiêu đề...",
      "content": "Nội dung markdown ngắn gọn về ngày 1..."
    }}
  ],
  "useful_phrases": [
    {{
      "vietnamese": "Chào bạn!",
      "translated": "Hello!",
      "pronunciation": "Chow bahn!"
    }}
  ]
}}
Không thêm bất kỳ chữ nào ngoài JSON Object này.
"""

        try:
            raw_output = self.model.generate_json(prompt)
            translation_data = json.loads(raw_output)
            state["final_translated"] = translation_data
        except Exception as e:
            print("Failed to parse Translate Agent output:", e)
            raise e
