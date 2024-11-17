import xml.etree.ElementTree as et
import regex
from tqdm import tqdm
import open_discourse.definitions.path_definitions as path_definitions
import logging

logging.basicConfig(level=logging.INFO)

# input directory
INPUT_PATH = path_definitions.DATA_CACHE / "electoral_term_pp20" / "stage_01"

# output directory
OUTPUT_PATH = path_definitions.DATA_CACHE / "electoral_term_pp20" / "stage_02"


def read_xml_file(xml_file_path):
    """Read and return the root of the XML file."""
    tree = et.parse(xml_file_path)
    return tree.getroot()


def save_xml(element_tree, save_path, file_name):
    """Save the given ElementTree to an XML file."""
    element_tree.write(save_path / file_name, encoding="UTF-8", xml_declaration=True)


def save_all_components(toc, session_content, appendix, meta_data, save_path):
    """Save all components to their respective XML files."""
    save_xml(toc, save_path, "toc.xml")
    save_xml(session_content, save_path, "session_content.xml")
    save_xml(appendix, save_path, "appendix.xml")
    save_xml(meta_data, save_path, "meta_data.xml")


def process_xml_file(xml_file_path):
    """Process a single XML file and return its components."""
    root = read_xml_file(xml_file_path)

    # Just process and return components
    toc = et.ElementTree(root.find("vorspann"))
    session_content = et.ElementTree(root.find("sitzungsverlauf"))
    appendix = et.ElementTree(root.find("anlagen"))
    meta_data = et.ElementTree(root.find("rednerliste"))

    return toc, session_content, appendix, meta_data


def save_xml_components(xml_file_path, components):
    """Save the components to files."""
    toc, session_content, appendix, meta_data = components
    # responsible for constructing a file path where processed XML components will be saved.
    save_path = OUTPUT_PATH / regex.search(r"\d+", xml_file_path.stem).group()
    save_path.mkdir(parents=True, exist_ok=True)
    save_all_components(toc, session_content, appendix, meta_data, save_path)


def main():
    for xml_file_path in tqdm(
        sorted(INPUT_PATH.glob("*.xml")), desc="Parsing term 20..."
    ):
        components = process_xml_file(xml_file_path)
        save_xml_components(xml_file_path, components)

        logging.info("Script 02_03 done.")


if __name__ == "__main__":
    main()
