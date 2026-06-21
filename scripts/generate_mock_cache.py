import json
import os

cache_dir = r"d:\AIDEV\data\cache"
os.makedirs(cache_dir, exist_ok=True)

# 1. Phú Quốc (4 days, 5000000 VND)
phu_quoc_state = {
    "agent_logs": [],
    "user_request": {
        "destination": "Phú Quốc",
        "days": 4,
        "budget_per_day": 5000000,
        "language": "Tiếng Việt",
        "has_kids": False,
        "preferences": "ở resort 5 sao sang trọng",
        "weather_sim_mode": "Nắng đẹp"
    },
    "itinerary": [
        {
            "day": 1,
            "session": "Sáng",
            "places": [
                {
                    "name": "VinWonders Phú Quốc",
                    "coordinate": {"lat": 10.3341, "lon": 103.8587},
                    "avg_duration": "4h",
                    "description": "Bắt đầu chuyến đi với công viên giải trí quy mô nhất Việt Nam."
                }
            ]
        },
        {
            "day": 1,
            "session": "Chiều",
            "places": [
                {
                    "name": "Grand World Phú Quốc",
                    "coordinate": {"lat": 10.3245, "lon": 103.8553},
                    "avg_duration": "3h",
                    "description": "Thành phố không ngủ, phù hợp chụp hình check-in và đi dạo thuyền Gondola."
                }
            ]
        },
        {
            "day": 1,
            "session": "Tối",
            "places": [
                {
                    "name": "Chợ đêm Phú Quốc",
                    "coordinate": {"lat": 10.2185, "lon": 103.9632},
                    "avg_duration": "2h",
                    "description": "Ăn tối hải sản tươi sống và mua đặc sản về làm quà."
                }
            ]
        },
        {
            "day": 2,
            "session": "Sáng",
            "places": [
                {
                    "name": "Hòn Thơm (Cáp treo)",
                    "coordinate": {"lat": 10.0152, "lon": 104.0154},
                    "avg_duration": "4h",
                    "description": "Trải nghiệm cáp treo vượt biển dài nhất thế giới và tắm biển Hòn Thơm."
                }
            ]
        },
        {
            "day": 2,
            "session": "Chiều",
            "places": [
                {
                    "name": "Bãi Sao",
                    "coordinate": {"lat": 10.0526, "lon": 104.0345},
                    "avg_duration": "2h",
                    "description": "Nghỉ ngơi và bơi lội tại một trong những bãi biển đẹp nhất Phú Quốc với cát trắng mịn."
                }
            ]
        },
        {
            "day": 2,
            "session": "Tối",
            "places": [
                {
                    "name": "Dạo biển đêm",
                    "coordinate": {"lat": 10.2112, "lon": 103.9602},
                    "avg_duration": "1.5h",
                    "description": "Nghỉ ngơi tại resort và dạo biển ban đêm."
                }
            ]
        },
        {
            "day": 3,
            "session": "Sáng",
            "places": [
                {
                    "name": "Nhà tù Phú Quốc",
                    "coordinate": {"lat": 10.0381, "lon": 104.0177},
                    "avg_duration": "1.5h",
                    "description": "Tìm hiểu lịch sử cách mạng hào hùng của dân tộc."
                },
                {
                    "name": "Nhà thùng nước mắm",
                    "coordinate": {"lat": 10.2223, "lon": 103.9631},
                    "avg_duration": "1h",
                    "description": "Tham quan quy trình làm nước mắm truyền thống."
                }
            ]
        },
        {
            "day": 3,
            "session": "Chiều",
            "places": [
                {
                    "name": "Sunset Sanato Beach Club",
                    "coordinate": {"lat": 10.1555, "lon": 103.9744},
                    "avg_duration": "2.5h",
                    "description": "Ngắm hoàng hôn tuyệt đẹp với các tiểu cảnh độc đáo."
                }
            ]
        },
        {
            "day": 3,
            "session": "Tối",
            "places": [
                {
                    "name": "Ăn tối nhà hàng sang trọng",
                    "coordinate": {"lat": 10.2185, "lon": 103.9632},
                    "avg_duration": "2h",
                    "description": "Tận hưởng bữa tối Fine-dining bên bờ biển."
                }
            ]
        },
        {
            "day": 4,
            "session": "Sáng",
            "places": [
                {
                    "name": "Vườn thú Safari Phú Quốc",
                    "coordinate": {"lat": 10.3341, "lon": 103.8821},
                    "avg_duration": "3h",
                    "description": "Khám phá vườn thú bán hoang dã lớn nhất Việt Nam."
                }
            ]
        },
        {
            "day": 4,
            "session": "Chiều",
            "places": [
                {
                    "name": "Trang trại ngọc trai",
                    "coordinate": {"lat": 10.1700, "lon": 103.9688},
                    "avg_duration": "1h",
                    "description": "Mua sắm trang sức ngọc trai cao cấp trước khi ra sân bay."
                }
            ]
        },
        {
            "day": 4,
            "session": "Tối",
            "places": [
                {
                    "name": "Sân bay Phú Quốc",
                    "coordinate": {"lat": 10.1652, "lon": 103.9961},
                    "avg_duration": "1h",
                    "description": "Lên máy bay trở về."
                }
            ]
        }
    ],
    "weather": {
        "alerts": [],
        "raw_data": {
            "description": "Trời nắng đẹp, thích hợp tắm biển.",
            "temp": 30.5
        }
    },
    "food_suggestions": {
        "meals": [
            {"time": "Bữa Sáng", "suggestion": "Bún quậy Kiến Xây - Đặc sản không thể bỏ lỡ.", "price_est": "50,000 VND"},
            {"time": "Bữa Trưa", "suggestion": "Gỏi cá trích, nhum biển nướng mỡ hành tại nhà hàng hải sản.", "price_est": "300,000 VND"},
            {"time": "Bữa Tối", "suggestion": "BBQ Hải sản cao cấp tại Resort 5 sao.", "price_est": "1,500,000 VND"}
        ]
    },
    "booking": {
        "hotel": {
            "name": "JW Marriott Phu Quoc Emerald Bay Resort & Spa",
            "type": "Resort 5 Sao",
            "rating": 4.9,
            "address": "Bãi Khem, Phú Quốc",
            "price_per_night": 7500000,
            "description": "Kiệt tác nghỉ dưỡng ven biển được thiết kế bởi Bill Bensley, phù hợp ngân sách cao cấp.",
            "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=800&auto=format&fit=crop"
        },
        "transport": {
            "type": "Xe Limousine đưa đón",
            "price_estimate": "1,500,000 VND/ngày",
            "provider_info": "Dịch vụ xe riêng VIP Phú Quốc",
            "description": "Xe sang trọng, tài xế riêng phục vụ suốt hành trình."
        }
    },
    "local_guide": {
        "cultural_notes": "Phú Quốc nổi tiếng với nước mắm và hồ tiêu. Hãy nhớ mua về làm quà.",
        "practical_tips": [
            "Mang theo kem chống nắng vì tia UV rất cao.",
            "Nên đặt vé VinWonders và Safari trước để tránh xếp hàng."
        ]
    },
    "final_translated": {
        "translated_itinerary": "Đã sử dụng bản gốc tiếng Việt (Demo Cache)."
    }
}

with open(os.path.join(cache_dir, "Phú_Quốc_4_5000000.json"), "w", encoding="utf-8") as f:
    json.dump(phu_quoc_state, f, ensure_ascii=False, indent=2)

print("Created mock cache for Phu Quoc!")
