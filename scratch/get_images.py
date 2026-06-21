import json
import urllib.request
import urllib.parse

places = [
    ("ky_co", "Ky Co Beach"),
    ("eo_gio", "Eo Gio"),
    ("hon_kho", "Hon Kho"),
    ("bai_quy_nhon", "Quy Nhon Beach"),
    ("ghenh_rang", "Ghenh Rang"),
    ("thap_doi", "Twin Towers Quy Nhon"),
    ("thap_banh_it", "Banh It Tower"),
    ("cau_thi_nai", "Thi Nai Bridge"),
    ("quang_truong", "Nguyen Tat Thanh Square Quy Nhon"),
    ("cho_dem", "Quy Nhon Night Market"),
    ("bai_dai", "Bai Dai Quy Nhon"),
    ("flc_beach", "FLC Quy Nhon")
]

def get_wiki_image(query):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        pages = data['query']['pages']
        for page_id in pages:
            if 'original' in pages[page_id]:
                return pages[page_id]['original']['source']
    except Exception as e:
        pass
    return None

results = {}
for id, query in places:
    img = get_wiki_image(query)
    if not img:
        # Try vietnamese
        img = get_wiki_image(query.replace(" Quy Nhon", "").replace(" Beach", " biển"))
    results[id] = img

print(json.dumps(results, indent=2))
