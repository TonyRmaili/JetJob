import requests
import json
import os

def search_ads(BASE_URL:str ,keywords:str,limit:int, offset:int,
            output_savepath:str, output_filename:str):
    # Search parameters
    params = {
        "q": keywords,      # Keyword search
        "limit": limit,        # Number of results to return
        "offset": offset    # Starting point of results
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
            first_hit = hits[0]

            # Save all parameters from the first hit to a file (pretty JSON format)

            save_path = os.path.join(output_savepath,output_filename)

            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(first_hit, f, ensure_ascii=False, indent=4)

        else:
            print("No job listings found for the given search parameters.")
    else:
        print(f"Request failed with status code: {response.status_code}")




if __name__ == "__main__":
    BASE_URL = "https://jobsearch.api.jobtechdev.se/search"

    search_ads(
        BASE_URL=BASE_URL,
        keywords="python",
        limit=1,
        offset=0,
        output_savepath= "./outputs",
        output_filename="test.json"
    )



