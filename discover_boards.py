# discover_boards.py (fetch from awesome-easy-apply GitHub only)
import json
import requests
import re

GH_FILE = "greenhouse_companies.json"
LEVER_FILE = "lever_companies.json"

REPO_RAW_URL = "https://raw.githubusercontent.com/sample-resume/awesome-easy-apply/main/README.md"


def extract_company_slugs():
    print("🔍 Fetching easy-apply company list...")
    gh_slugs = set()
    lever_slugs = set()
    try:
        res = requests.get(REPO_RAW_URL)
        lines = res.text.splitlines()
        for line in lines:
            gh_match = re.search(r"boards\.greenhouse\.io/([a-zA-Z0-9\-]+)", line)
            if gh_match:
                gh_slugs.add(gh_match.group(1))

            lever_match = re.search(r"jobs\.lever\.co/([a-zA-Z0-9\-]+)", line)
            if lever_match:
                lever_slugs.add(lever_match.group(1))
    except Exception as e:
        print(f"❌ Error fetching or parsing list: {e}")

    return sorted(gh_slugs), sorted(lever_slugs)


def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def main():
    greenhouse, lever = extract_company_slugs()
    print(f"✅ Found {len(greenhouse)} Greenhouse slugs")
    print(f"✅ Found {len(lever)} Lever slugs")

    save_json(greenhouse, GH_FILE)
    save_json(lever, LEVER_FILE)


if __name__ == "__main__":
    main()