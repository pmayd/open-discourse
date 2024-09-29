import time

import regex
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

import open_discourse.definitions.path_definitions as path_definitions

# output directory
OUTPUT_PATH = path_definitions.DATA_CACHE / "electoral_term_20" / "stage_01"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

election_periods = [
    {
        "election_period": 20,
        "url": "https://www.bundestag.de/ajax/filterlist/de/services/opendata/866354-866354?offset={}",
    },
]

for election_period in election_periods:
    print(
        f"Scraping links for term {election_period['election_period']}...",
        end="",
        flush=True,
    )

    offset = 0
    xml_links = []

    while True:
        URL = election_period["url"].format(str(offset))
        page = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.text, "html.parser")
        # scrape for links
        current_links = list(soup.find_all("a", attrs={"href": regex.compile("xml$")}))
        if len(current_links) != 0:
            xml_links += current_links
            offset += len(current_links)
        else:
            break

    print("Done.")

    for link in tqdm(
        xml_links,
        desc=f"Download XML-files for term {election_period['election_period']}...",
    ):
        url = "https://www.bundestag.de" + link.get("href")
        page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        session = regex.search(r"\d{5}(?=\.xml)", url).group(0)

        with open(OUTPUT_PATH / (session + ".xml"), "w") as file:
            file.write(
                regex.sub(
                    "</sub>",
                    "",
                    regex.sub("<sub>", "", page.content.decode("utf-8")),
                )
            )
        time.sleep(1)

assert OUTPUT_PATH.exists()
assert (
    len(list(OUTPUT_PATH.glob("*.xml"))) > 0
), "At least one XML file should be downloaded."

print("Script 01_03 done.")
