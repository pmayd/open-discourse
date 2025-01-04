import io
import zipfile

import regex
import requests
from tqdm import tqdm

from open_discourse.definitions import path_definitions

# output directory
RAW_XML = path_definitions.RAW_XML

zip_links = [
    "https://www.bundestag.de/resource/blob/487966/4078f01fb3198dc3cee8945d6db3b231/pp01.zip",
    "https://www.bundestag.de/resource/blob/487968/5792895a5cf4ab51ed94c77157297031/pp02.zip",
    "https://www.bundestag.de/resource/blob/487970/1c737594587745b399e84bc30f049d69/pp03.zip",
    "https://www.bundestag.de/resource/blob/488216/3b20f8dd5efad2cafa3fb0b6df24cbb9/pp04.zip",
    "https://www.bundestag.de/resource/blob/488218/bfba1a02d1090efc873f9a60f318a162/pp05.zip",
    "https://www.bundestag.de/resource/blob/488220/b2b4d0d49600ef852d15e4052fabce1e/pp06.zip",
    "https://www.bundestag.de/resource/blob/488222/b10bae395e887aac9ac08afbd1da62fc/pp07.zip",
    "https://www.bundestag.de/resource/blob/490390/dfcac024ce8e548774e16f03c36293e2/pp08.zip",
    "https://www.bundestag.de/resource/blob/490382/effcc03f3b3e157f9d8050b4a9d9d089/pp09.zip",
    "https://www.bundestag.de/resource/blob/490374/07ce06f666b624d37b47d2fe6e205ab4/pp10.zip",
    "https://www.bundestag.de/resource/blob/490384/ad57841a599aba6faa794174e53a8797/pp11.zip",
    "https://www.bundestag.de/resource/blob/490376/8775517464dccd8660eb96446d18dd26/pp12.zip",
    "https://www.bundestag.de/resource/blob/490388/84914a1feff6f2f4988ce352a5500845/pp13.zip",
    "https://www.bundestag.de/resource/blob/490380/c4ca5488b447668f802039f1f769b278/pp14.zip",
    "https://www.bundestag.de/resource/blob/490394/08411d0257e9e07daef24001a958db53/pp15.zip",
    "https://www.bundestag.de/resource/blob/490386/80886372e6bbe903dd4d7eb03fe424b3/pp16.zip",
    "https://www.bundestag.de/resource/blob/490378/033276846771aac12dd7109724a1134b/pp17.zip",
    "https://www.bundestag.de/resource/blob/490392/90738376bb195628b95d117ab5392cfe/pp18.zip",
    "https://www.bundestag.de/resource/blob/870686/91b713c492499db98eec5b2f8f142d20/pp19.zip",
]


class MockLogger:
    def __init__(self, verbose=True):
        self.verbose = verbose

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
    logger.info("Begin task 01_01, download electoral term data...")
    for link in tqdm(zip_links, desc="Download & unzip election period data..."):
        try:
            # Extract election period from URL
            electoral_term_str = "electoral_term_" + regex.search(
                r"pp(\d+).zip$", link
            ).group(0)

            print(f"Download & unzip '{electoral_term_str}'...", end="", flush=True)

            r = requests.get(link)

            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                save_path = RAW_XML / electoral_term_str
                save_path.mkdir(parents=True, exist_ok=True)
                z.extractall(save_path)
            logger.info(f"Downloaded '{link}' to '{save_path}'")
        except Exception as e:
            logger.error(f"Error downloading '{link}': {e}")

    try:
        assert RAW_XML.exists()
        assert len(list(RAW_XML.glob("*"))) == len(zip_links)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise e
    logger.info("Task 01_01 completed.")
