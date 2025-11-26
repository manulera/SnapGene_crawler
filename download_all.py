import json
import requests
import os
import time

with open("index.json", "r") as f:
    data = json.load(f)

download_count = 0
for category_path, category in data.items():

    if not os.path.isdir(f"downloaded/{category_path}"):
        os.makedirs(f"downloaded/{category_path}", exist_ok=True)

    for plasmid in category["plasmids"]:
        out_name = f"downloaded/{category_path}/{plasmid['subpath']}.dna"
        if os.path.exists(out_name):
            print(f"Skipping {plasmid['name']} because it already exists")
            continue

        print(f"Downloading {plasmid['name']}")
        url = f"https://www.snapgene.com/local/fetch.php?set={category_path}&plasmid={plasmid['subpath']}"
        print(url)
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to download {plasmid['name']}")

        with open(out_name, "wb") as f:
            f.write(response.content)

        download_count += 1

        if download_count > 200:
            print("Waiting 2 minutes to avoid rate limiting")
            # Wait 2 minutes
            time.sleep(120)
            download_count = 0
