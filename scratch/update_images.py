import json

def update_json_file(filepath, mapping):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if "Quy Nhơn" in data and isinstance(data["Quy Nhơn"], list):
        for item in data["Quy Nhơn"]:
            if isinstance(item, dict) and item.get("id") in mapping:
                item["image_url"] = mapping[item["id"]]
    
    # booking_data has different structure
    if filepath.endswith('booking_data.json') and "Quy Nhơn" in data:
        if "accommodations" in data["Quy Nhơn"]:
            for item in data["Quy Nhơn"]["accommodations"]:
                if item.get("id") in mapping:
                    item["image_url"] = mapping[item["id"]]
                    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

places_images = {
    "ky_co": "https://ik.imagekit.io/tvlk/blog/2022/08/bai-bien-ky-co-1.jpg",
    "eo_gio": "https://ik.imagekit.io/tvlk/blog/2022/08/eo-gio-quy-nhon-1.jpg",
    "hon_kho": "https://ik.imagekit.io/tvlk/blog/2022/08/dao-hon-kho-1.jpg",
    "bai_quy_nhon": "https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/bai-bien-quy-nhon-1.jpg",
    "ghenh_rang": "https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/ghenh-rang-tien-sa-1.jpg",
    "thap_doi": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Th%C3%A1p_%C4%90%C3%B4i_Quy_Nh%C6%A1n.jpg",
    "thap_banh_it": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Th%C3%A1p_B%C3%A1nh_%C3%8Dt_1.jpg",
    "cau_thi_nai": "https://upload.wikimedia.org/wikipedia/commons/4/4e/C%E1%BA%A7u_Th%E1%BB%8B_N%E1%BA%A1i.jpg",
    "quang_truong": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Qu%E1%BA%A3ng_tr%C6%B0%E1%BB%9Dng_Nguy%E1%BB%85n_T%E1%BA%A5t_Th%C3%A0nh%2C_TP_Quy_Nh%C6%A1n.jpg",
    "cho_dem": "https://bazantravel.com/cdn/medias/uploads/58/58882-cho-dem-quy-nhon-4-700x466.jpg",
    "bai_dai": "https://cdn3.ivivu.com/2014/10/bai-dai-quy-nhon.jpg",
    "flc_beach": "https://flc.vn/wp-content/uploads/2020/06/flc-quy-nhon.jpg"
}

hotels_images = {
    "flc_city": "https://pix8.agoda.net/hotelImages/28135832/-1/50cd21262ab0ff124d3393ecde73082a.jpg",
    "anya_premier": "https://pix8.agoda.net/hotelImages/11252906/-1/88df0a2cb7034c2cbb41e97de9ba5ec9.jpg",
    "mira_baixep": "https://pix8.agoda.net/hotelImages/15694294/-1/2ea6a77d7be0eecf2b904c00f7e435cf.jpg",
    "kura_homestay": "https://pix8.agoda.net/hotelImages/10547037/-1/2d0cdba47565ccbc4d46cfcd7a641a99.jpg",
    "john_paul": "https://cf.bstatic.com/xdata/images/hotel/max1024x768/221376092.jpg?k=12345",
    "life_backpacker": "https://cf.bstatic.com/xdata/images/hotel/max1024x768/193257850.jpg?k=54321",
    "fleur_de_lys": "https://pix8.agoda.net/hotelImages/10545937/-1/948fb1e19488e0b65f04b2a88ba88f34.jpg",
    "avani": "https://pix8.agoda.net/hotelImages/10667/-1/3c1d9539a2d718b5b5c9dc76717a6a42.jpg",
    "crown_retreat": "https://pix8.agoda.net/hotelImages/4873177/-1/80b59b15cd09dc756df8f7dfc02287f3.jpg"
}

food_images = {
    "gia_vy": "https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/banh-xeo-tom-nhay-1.jpg",
    "phuong_teo": "https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/bun-cha-ca-1.jpg",
    "thuy_kieu": "https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/oc-thuy-kieu.jpg",
    "bep_nha_1989": "https://quynhontourist.com/wp-content/uploads/2019/10/bep-nha-1989.jpg",
    "tre_restaurant": "https://quynhontourist.com/wp-content/uploads/2019/10/nha-hang-tre-quy-nhon.jpg",
    "hoa_hoa": "https://quynhontourist.com/wp-content/uploads/2019/10/nha-hang-hoa-hoa-quy-nhon.jpg",
    "hai_sy": "https://quynhontourist.com/wp-content/uploads/2019/10/hai-san-hai-sy.jpg",
    "banh_hoi_dien_hong": "https://quynhontourist.com/wp-content/uploads/2019/10/banh-hoi-chao-long.jpg"
}

update_json_file('data/places_data.json', places_images)
update_json_file('data/booking_data.json', hotels_images)
update_json_file('data/restaurants_data.json', food_images)

print("Updated json files with realistic images.")
