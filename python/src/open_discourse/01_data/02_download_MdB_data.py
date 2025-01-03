import io
import zipfile

import requests

from open_discourse.definitions import path_definitions

mp_base_data_link = "https://www.bundestag.de/resource/blob/472878/7d4d417dbb7f7bd44508b3dc5de08ae2/MdB-Stammdaten-data.zip"

print("Download & unzip 'MP_BASE_DATA'...", end="", flush=True)

r = requests.get(mp_base_data_link)

with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    mp_base_data_path = path_definitions.DATA_RAW / "MP_BASE_DATA"
    mp_base_data_path.mkdir(parents=True, exist_ok=True)

    z.extractall(mp_base_data_path)

assert (mp_base_data_path / "MDB_STAMMDATEN.XML").exists()

print("Script 01_02 done.")
