#!/usr/bin/env python3
"""
PC Builder Link Generator for Top Vietnamese Retailers
Generates direct URLs for PC Configurator pages and keyword search links.
"""

import urllib.parse
import sys
import json

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

RETAILER_BUILDERS = {
    "anphat": {
        "name": "An Phát Computer",
        "builder_url": "https://www.anphatpc.com.vn/xay-dung-cau-hinh-pc.html",
        "search_pattern": "https://www.anphatpc.com.vn/tim?q={query}",
        "prebuilt_category": "https://www.anphatpc.com.vn/may-tinh-choi-game-pc-gaming.html"
    },
    "gearvn": {
        "name": "GearVN",
        "builder_url": "https://gearvn.com/pages/build-pc",
        "search_pattern": "https://gearvn.com/search?type=product&q={query}",
        "prebuilt_category": "https://gearvn.com/collections/pc-gvn"
    },
    "hacom": {
        "name": "HACOM",
        "builder_url": "https://hacom.vn/xay-dung-cau-hinh-pc",
        "search_pattern": "https://hacom.vn/tim?q={query}",
        "prebuilt_category": "https://hacom.vn/pc-gaming"
    },
    "kccshop": {
        "name": "KCCShop",
        "builder_url": "https://kccshop.vn/build-pc/",
        "search_pattern": "https://kccshop.vn/?s={query}&post_type=product",
        "prebuilt_category": "https://kccshop.vn/may-tinh-de-ban/"
    },
    "nguyencong": {
        "name": "Nguyễn Công PC",
        "builder_url": "https://nguyencongpc.vn/buildpc",
        "search_pattern": "https://nguyencongpc.vn/tim-kiem?q={query}",
        "prebuilt_category": "https://nguyencongpc.vn/bo-pc"
    },
    "memoryzone": {
        "name": "MemoryZone",
        "builder_url": "https://memoryzone.com.vn",
        "search_pattern": "https://memoryzone.com.vn/tim-kiem?q={query}",
        "prebuilt_category": "https://memoryzone.com.vn/pc-may-tinh-de-ban"
    }
}

def generate_links(query_terms):
    results = {}
    encoded_query = urllib.parse.quote_plus(" ".join(query_terms))
    for key, data in RETAILER_BUILDERS.items():
        results[key] = {
            "name": data["name"],
            "builder_page": data["builder_url"],
            "search_url": data["search_pattern"].format(query=encoded_query),
            "prebuilt_url": data["prebuilt_category"]
        }
    return results

if __name__ == "__main__":
    query = sys.argv[1:] if len(sys.argv) > 1 else ["i5", "13500", "1650", "32gb"]
    links = generate_links(query)
    print(json.dumps(links, ensure_ascii=False, indent=2))
