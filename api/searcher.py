import requests
import json
import os
from datetime import datetime


def multi_search(keywords: list[str], BASE_URL: str, limit: int, offset: int, filter_key: str, output_path: str):
    seen_ids = set()
    unique_ads = []

    for keyword in keywords:
        hits = search_ads(BASE_URL, keyword, limit, offset)
        if hits:
            for ad in hits:
                ad_id = ad.get("id")
                if ad_id and ad_id not in seen_ids:
                    seen_ids.add(ad_id)
                    unique_ads.append(ad)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    joined_keywords = "_".join(keywords)

    matched_ads, non_matched_ads = split_by_keyword_full_objects(data=unique_ads, keyword=filter_key)

    matched_dir = os.path.join(output_path, f"matched_{filter_key}")
    unmatched_dir = os.path.join(output_path, f"unmatched_{filter_key}")

    os.makedirs(matched_dir, exist_ok=True)
    os.makedirs(unmatched_dir, exist_ok=True)

    filename = f"{timestamp}_{joined_keywords}.json"

    # Save matched ads
    with open(os.path.join(matched_dir, filename), "w", encoding="utf-8") as f:
        json.dump(matched_ads, f, indent=2, ensure_ascii=False)

    # Save unmatched ads
    with open(os.path.join(unmatched_dir, filename), "w", encoding="utf-8") as f:
        json.dump(non_matched_ads, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(matched_ads)} matched and {len(non_matched_ads)} unmatched ads.")


def search_ads(BASE_URL:str ,keyword:str,limit:int, offset:int) -> list:
    # Search parameters
    params = {
    "q": keyword,             
    "limit": limit,                
    "offset": offset                 
    }

    # Make the GET request
    response = requests.get(BASE_URL , params= params)
   
    # Check for successful response
    if response.status_code == 200:
        data = response.json()
        hits = data.get("hits", [])

        if hits:
           return hits
        else:
            print("No job listings found for the given search parameters.")
    else:
        print(f"Request failed with status code: {response.status_code}")


def contains_keyword(obj,keyword):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if keyword in key.lower() and value:
                return True
            if contains_keyword(value, keyword):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if contains_keyword(item ,keyword):
                return True
    return False


def split_by_keyword_full_objects(data, keyword):
    with_keyword = []
    without_keyword = []

    for entry in data:
        if contains_keyword(entry, keyword):
            with_keyword.append(entry)
        else:
            without_keyword.append(entry)

    return with_keyword, without_keyword




if __name__ == "__main__":
    BASE_URL = "https://jobsearch.api.jobtechdev.se/search"
    keywords = ["python","machine learning"]


    multi_search(
        keywords=keywords,
        BASE_URL=BASE_URL,
        limit=10,
        offset=0,
        filter_key="email",
        output_path="./outputs"
    )
 