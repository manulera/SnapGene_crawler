from bs4 import BeautifulSoup
import requests
import json
import yaml


def check_robots_txt():
    url = "https://www.snapgene.com/robots.txt"
    response = requests.get(url)
    # Check that we can scrape
    if response.status_code != 200:
        raise Exception(f"Failed to scrape robots.txt: {response.status_code}")

    if "User-agent: *" not in response.text:
        raise Exception("User-agent * not found in robots.txt")

    disallowed_paths = []
    for line in response.text.split("\n"):
        if line.startswith("Disallow:"):
            disallowed_paths.append(line.split(" ")[1])

    print(*disallowed_paths, sep="\n")
    # If any disallowed path starts with /plasmids, raise an exception
    if any(path.startswith("/plasmids") for path in disallowed_paths):
        raise Exception("Disallowed path /plasmids found in robots.txt")

    print("\033[92m🤖 All good! we can crawl\033[0m")


def get_plasmid_category_links():
    url = "https://www.snapgene.com/plasmids"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    out_dict = dict()

    # Find the section with class landing-simple-section that contains the plasmid categories
    sections = soup.find_all("section", class_="landing-simple-section")
    for section in sections:
        # Look for a heading with "Plasmid Sets" to identify the correct section
        heading = section.find("h2", string="Plasmid Sets")
        if heading:
            # Find all links with class "link" within that section
            for link_element in section.find_all("a", class_="link"):
                subpath = link_element["href"].split("/")[-1]
                name = link_element.text.strip()
                out_dict[subpath] = {"name": name, "plasmids": []}
            break

    # Crawl each of the plasmid categories and get the plasmids
    for subpath, data in out_dict.items():
        print(f"> crawling {data['name']}")
        url = f"https://www.snapgene.com/plasmids/{subpath}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        sections = soup.find_all("section", class_="landing-simple-section")

        for section in sections:
            # Look for a heading with "Plasmid Sets" to identify the correct section
            heading = section.find("h2", string="Individual Sequences & Maps")
            if heading:
                # Find all links with class "link" within that section
                for link_element in section.find_all("a", class_="link"):
                    subpath = link_element["href"].split("/")[-1]
                    name = link_element.text.strip()
                    data["plasmids"].append({"name": name, "subpath": subpath})
                break

    return out_dict


if __name__ == "__main__":
    check_robots_txt()
    category_links = get_plasmid_category_links()
    for category_path, category in category_links.items():
        category["plasmids"].sort(key=lambda x: x["name"].lower())

    with open("index.json", "w") as f:
        json.dump(category_links, f, indent=2)
    with open("index.yaml", "w") as f:
        yaml.dump(category_links, f, sort_keys=False)
