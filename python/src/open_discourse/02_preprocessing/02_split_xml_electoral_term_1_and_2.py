import xml.etree.ElementTree as et

import dicttoxml
from tqdm import tqdm

import open_discourse.definitions.path_definitions as path_definitions
from open_discourse.helper_functions.clean_text import clean
from open_discourse.helper_functions.parser import get_doc_metadata, get_session_content
from open_discourse.helper_functions.utils import get_term_from_path

# input directory
RAW_XML = path_definitions.RAW_XML

# output directory
RAW_TXT = path_definitions.RAW_TXT
RAW_TXT.mkdir(parents=True, exist_ok=True)

# Open every xml plenar file in every electoral term.
for folder_path in sorted(RAW_XML.iterdir()):
    # Skip e.g. the .DS_Store file.

    if not folder_path.is_dir():
        continue

    term_number = get_term_from_path(str(folder_path))
    if term_number is None:
        print(f"No term number found in {folder_path.stem}.")
        continue

    if term_number > 2:
        continue

    for xml_file_path in tqdm(
        list(folder_path.iterdir()), desc=f"Parsing term {term_number:>2}..."
    ):
        if xml_file_path.suffix == ".xml":
            tree = et.parse(xml_file_path)

            meta_data = get_doc_metadata(tree)
            text_corpus = tree.find("TEXT").text

            # Clean text corpus.
            text_corpus = clean(text_corpus)

            # Append "END OF FILE" to document text, otherwise pattern is
            # not found, when appearing at the end of the file.
            text_corpus += "\n\nEND OF FILE"

            session_content = get_session_content(text_corpus)

            if not session_content:
                print(f"No session content found in {xml_file_path.stem}.")
                continue

            save_path = RAW_TXT / folder_path.stem / xml_file_path.stem
            save_path.mkdir(parents=True, exist_ok=True)
            # Save table of content, spoken content and appendix
            # in separate folders.
            with open(save_path / "session_content.txt", "w") as text_file:
                text_file.write(session_content)

            with open(save_path / "meta_data.xml", "wb") as result_file:
                result_file.write(dicttoxml.dicttoxml(meta_data.dict()))

assert RAW_TXT.exists(), f"Output directory {RAW_TXT} does not exist."
assert (
    len(list(RAW_TXT.glob("*_pp*"))) == len(list(RAW_XML.glob("*.zip")))
), "Number of directories in output directory is not equal to number of directories in input directory"

print("Script 02_02 done.")
