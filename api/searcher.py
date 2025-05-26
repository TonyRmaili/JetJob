import requests
import json
import os

def search_ads(BASE_URL:str ,keyword:str,limit:int, offset:int,
            output_savepath:str, output_filename:str):
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
            # for job in hits:
            #     headline = job.get("headline", "No headline provided")
            #     municipality = job.get("workplace_address", {}).get("municipality", "No municipality provided")
            #     employer = job.get("employer", {}).get("name", "No employer provided")
            #     print(f"Job Title: {headline}\nLocation: {municipality}\nEmployer: {employer}\n")
            # first_hit = hits[0]

            # Save all parameters from the first hit to a file (pretty JSON format)

            save_path = os.path.join(output_savepath,output_filename)

            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(hits, f, ensure_ascii=False, indent=4)

        else:
            print("No job listings found for the given search parameters.")
    else:
        print(f"Request failed with status code: {response.status_code}")

def format_response(path,response):
    pass

def sort_response(path):
    with open(path,encoding='utf-8') as f:
        response = json.load(f)
    email_fields = find_email_keys(response)

    for path, value in email_fields:
        print(f"Found: {path} => {value}")

def find_email_keys(obj, path=""):
    results = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_path = f"{path}.{key}" if path else key
            if "email" in key.lower():
                results.append((full_path, value))
            results.extend(find_email_keys(value, full_path))

    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            full_path = f"{path}[{idx}]"
            results.extend(find_email_keys(item, full_path))

    return results

def find_email_objects(obj, email_key_match="email", path=""):
    results = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if email_key_match.lower() in key.lower():
                results.append((obj, path))  # Save the object itself and its path
                break  # Only need one matching key to include the object
        for key, value in obj.items():
            results.extend(find_email_objects(value, email_key_match, f"{path}.{key}" if path else key))

    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            results.extend(find_email_objects(item, email_key_match, f"{path}[{idx}]"))

    return results


def save_objects_by_email_presence(json_data, output_base_path):
    found_objects = find_email_objects(json_data)

    present_folder = os.path.join(output_base_path, "has_email")
    none_folder = os.path.join(output_base_path, "missing_email")

    os.makedirs(present_folder, exist_ok=True)
    os.makedirs(none_folder, exist_ok=True)

    count_present = 0
    count_none = 0

    for i, (obj, path) in enumerate(found_objects):
        # Find the first email-like key in the object
        email_value = next((v for k, v in obj.items() if "email" in k.lower()), None)

        if email_value is None:
            out_path = os.path.join(none_folder, f"object_{count_none}.json")
            count_none += 1
        else:
            out_path = os.path.join(present_folder, f"object_{count_present}.json")
            count_present += 1

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=4)

    print(f"Saved {count_present} with email and {count_none} with missing email.")


if __name__ == "__main__":
    BASE_URL = "https://jobsearch.api.jobtechdev.se/search"

    path = "./outputs/test.json"

    # sort_response(path=path)

    # with open(path, "r", encoding="utf-8") as f:
    #     data = json.load(f)

    # save_objects_by_email_presence(data, "./sorted_email_objects")


    search_ads(
        BASE_URL=BASE_URL,
        
        keyword="python",
        limit=10,
        offset=0,

        output_savepath= "./outputs",
        output_filename="test_muni1280.json"
    )



