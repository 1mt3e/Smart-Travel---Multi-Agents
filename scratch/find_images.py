import urllib.request
import re
import json

keywords = [
    "vietnamese noodle soup",  # Bún chả cá
    "vietnamese pork dish",   # Bánh hỏi lòng heo
    "vietnamese spring rolls", # Chả ram tôm đất
    "vietnamese pancake crepes",     # Bánh xèo tôm nhảy
    "seafood soup congee",     # Cháo sứa
    "seafood lobster crab",    # Hải sản tươi sống
    "grilled seafood beach",   # Hải sản nướng biển
    "vietnamese grilled pork", # Nem nướng Quy Nhơn
    "vietnamese coffee phin",  # Café Đông Dương
    "bun bo hue beef soup",    # Bún bò Quy Nhơn
    "vietnamese chicken rice", # Cơm gà Quy Nhơn
    "seafood hotpot"           # Lẩu hải sản
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

results = {}

for kw in keywords:
    query = urllib.parse.quote(kw)
    url = f"https://unsplash.com/s/photos/{query}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            # Look for photo URLs in the HTML
            # Unsplash has images like https://images.unsplash.com/photo-15...
            matches = re.findall(r'https://images.unsplash.com/photo-[0-9a-zA-Z\-]+', html)
            # Dedup and pick the first few
            seen = set()
            urls = []
            for m in matches:
                if m not in seen:
                    seen.add(m)
                    # Add query params for good resolution and cropping
                    urls.append(f"{m}?q=80&w=800&auto=format&fit=crop")
            results[kw] = urls[:5]
            print(f"Found {len(urls)} images for keyword: {kw}")
    except Exception as e:
        print(f"Error searching for {kw}: {e}")

# Save results
with open("d:/AIDEV/scratch/unsplash_images.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Done!")
