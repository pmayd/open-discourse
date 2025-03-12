import time

import regex
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

import open_discourse.definitions.path_definitions as path_definitions

# output directory
OUTPUT_PATH = path_definitions.DATA_CACHE / "electoral_term_pp20" / "stage_01"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

election_periods = [
    {
        "election_period": 20,
        "url": "https://www.bundestag.de/ajax/filterlist/de/services/opendata/866354-866354?offset={}",
    },
]


class MockLogger:
    def info(self, msg):
        if self.verbose:
            print(msg)

    def error(self, msg):
        if self.verbose:
            print(msg)

    def warning(self, msg):
        if self.verbose:
            print(msg)


if __name__ == "__main__":
    logger = MockLogger()
    logger.info(
        f"Begin task 01_03, download raw data for electoral term(s) {list(election_periods.keys())} ..."
    )
    for election_period in election_periods:
        logger.info(
            f"Script 01_03. Scraping links for term {election_period['election_period']}..."
        )

        offset = 0
        xml_links = []

        while True:
            try:
                URL = election_period["url"].format(str(offset))
                page = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(page.text, "html.parser")
                # scrape for links
                current_links = list(
                    soup.find_all("a", attrs={"href": regex.compile("xml$")})
                )
                if len(current_links) != 0:
                    xml_links += current_links
                    offset += len(current_links)
                else:
                    break
            except Exception as e:
                logger.error(
                    f"Error getting links for parliamentary sessions from {URL}, {e}"
                )
                break
        print("Done.")

        for link in tqdm(
            xml_links,
            desc=f"Download XML-files for term {election_period['election_period']}...",
        ):
            try:
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
            except Exception as e:
                logger.error(f"Error downloading xml file from {url}: {e}")
    try:
        assert OUTPUT_PATH.exists()
        assert (
            len(list(OUTPUT_PATH.glob("*.xml"))) > 0
        ), "At least one XML file should be downloaded."
    except Exception as e:
        logger.error(f"Error: {e}")
        raise e
    logger.info("Done with task 01_03.")
