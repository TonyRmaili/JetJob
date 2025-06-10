import requests
import json
import os
import re


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

    matched_ads, non_matched_ads = split_by_keyword_full_objects(data=unique_ads, keyword=filter_key)

    matched_dir = os.path.join(output_path, f"matched_{filter_key}")
    unmatched_dir = os.path.join(output_path, f"unmatched_{filter_key}")

    os.makedirs(matched_dir, exist_ok=True)
    os.makedirs(unmatched_dir, exist_ok=True)

    sort_by_region(obj=matched_ads,path=matched_dir)
    sort_by_region(obj=non_matched_ads,path=unmatched_dir)


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

def get_unique_path(path):
    """Generate a unique filename by appending a counter if needed."""
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    i = 1
    while True:
        new_path = f"{base}_{i:02d}{ext}"
        if not os.path.exists(new_path):
            return new_path
        i += 1

def sort_by_region(path,obj):
    for ad in obj:
        region = ad["workplace_address"]["region"]
        headline = ad["headline"]
        headline = sanitize_filename(headline)
        
        if region:
            folder_path = os.path.join(path,region)
        else:
            folder_path = os.path.join(path,"region_missing")

        os.makedirs(folder_path,exist_ok=True)

        save_path = os.path.join(folder_path,headline+".json")
        save_path = get_unique_path(save_path)
        save_json(obj=ad,path=save_path)


def sanitize_filename(name: str) -> str:
    name = name.strip()  # Remove leading/trailing whitespace
    name = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', name)  # Replace invalid characters with _
    name = re.sub(r'\s+', '_', name)  # Replace internal whitespace with _
    return name


def save_json(obj,path):
    with open(path,'w',encoding="utf-8") as f:
        json.dump(obj,f,indent=4, ensure_ascii=False)


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
 