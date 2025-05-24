import requests
import json

# Base URL for JobSearch API
BASE_URL = "https://jobsearch.api.jobtechdev.se/search"

# Search parameters
params = {
    "q": "python",      # Keyword search
    "limit": 1,        # Number of results to return
    "offset": 0    # Starting point of results
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
        with open("first_job_ad.json", "w", encoding="utf-8") as f:
            json.dump(first_hit, f, ensure_ascii=False, indent=4)


    else:
        print("No job listings found for the given search parameters.")
else:
    print(f"Request failed with status code: {response.status_code}")




