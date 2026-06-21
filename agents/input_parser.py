import json
from config import UTILITY_MODEL
from agents.gemini_helper import GeminiHelper

class InputParserAgent:
    def __init__(self, gemini_key):
        self.gemini_key = gemini_key
        self.model = GeminiHelper(
            api_key=self.gemini_key,
            model_name=UTILITY_MODEL,
            system_instruction=(
                "Bạn là một trợ lý ảo thông minh chuyên phân tích yêu cầu du lịch của người dùng. "
                "Nhiệm vụ của bạn là đọc một đoạn văn bản yêu cầu và trích xuất các thông tin sau thành một JSON object hợp lệ: "
                "1. 'destination': Địa điểm du lịch mà người dùng muốn đến (trích xuất chính xác tên, ví dụ: Đà Lạt, Phú Quốc, Quy Nhơn...). Mặc định là Quy Nhơn nếu không rõ. "
                "2. 'days': Số ngày (int, từ 1 đến 5). Mặc định là 2 nếu không rõ. "
                "3. 'budget_per_day': Ngân sách mỗi ngày tính theo VND (int). Ví dụ: 2 triệu = 2000000. Mặc định là 1500000 nếu không rõ. "
                "4. 'has_kids': Có trẻ em đi cùng hay không (boolean). Mặc định là false. "
                "5. 'language': Ngôn ngữ hiển thị (chuỗi: 'Tiếng Việt', 'English', 'Chinese', 'Korean', 'Japanese'). Mặc định là 'Tiếng Việt'. "
                "6. 'preferences': Yêu cầu đặc biệt hoặc sở thích (chuỗi). Trích xuất các ý muốn ăn uống, phong cảnh, sở thích di chuyển."
                "Trả về duy nhất 1 chuỗi JSON, không có bất kỳ ký tự hoặc định dạng Markdown nào khác bao quanh."
            ),
        )

    def parse(self, user_input):
        prompt = f"""
Phân tích yêu cầu du lịch sau và trích xuất thông tin dưới dạng JSON:
"{user_input}"

Cấu trúc JSON mong muốn:
{{
  "destination": "Quy Nhơn",
  "days": 3,
  "budget_per_day": 2000000,
  "has_kids": true,
  "language": "Tiếng Việt",
  "preferences": "Thích ăn hải sản, ngắm hoàng hôn, tránh đi bộ nhiều."
}}
"""
        try:
            raw_output = self.model.generate_json(prompt)
            data = json.loads(raw_output)
            # Validate basic types to avoid crash
            data["destination"] = str(data.get("destination", "Quy Nhơn"))
            data["days"] = max(1, min(5, int(data.get("days", 2))))
            data["budget_per_day"] = int(data.get("budget_per_day", 1500000))
            data["has_kids"] = bool(data.get("has_kids", False))
            data["language"] = str(data.get("language", "Tiếng Việt"))
            data["preferences"] = str(data.get("preferences", ""))
            return data
        except Exception as e:
            print("Failed to parse user input:", e)
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                raise Exception("Hệ thống AI của Google đang bị quá tải do hết Quota (Lỗi 429). Vui lòng đợi khoảng 1 phút rồi thử lại!")
            raise Exception("Không thể phân tích yêu cầu của bạn lúc này. Vui lòng thử lại!")
