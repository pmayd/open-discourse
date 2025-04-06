# Python

The python service processes and creates all of the open-discourse data

## Folders

- The `data` folder contains all of the cached data
- The `src/open_discourse` folder contains all of the python scripts. More information on these can be found in the [README in src](./src/open_discourse/README.md)

## Data Processing Pipeline

The Python component of Open Discourse implements a multi-stage data processing pipeline that:

1. Downloads raw XML data from the Bundestag and scrapes supplementary data
2. Preprocesses and cleans the data
3. Extracts structured information (speeches, politicians, factions, etc.)
4. Processes and transforms the data for analysis
5. Loads the final data into a database

### Data Formats and Conversion

The pipeline processes data through several formats:

1. **XML files**: Raw data from the Bundestag (speeches, MP information)
2. **pandas DataFrames**: In-memory data structures for processing 
3. **PKL (pickle) files**: Serialized DataFrames stored as intermediate outputs
4. **CSV files**: Final output format for database loading

During preprocessing:
- The `extract_mps_from_mp_base_data.py` script extracts MP data from XML files and converts it into pandas DataFrames
- These DataFrames are serialized as PKL files for efficient storage between processing steps
- Government member data is scraped from Wikipedia and also stored as DataFrames/PKL files
- The two datasets (MPs and government members) are later merged to create a comprehensive politicians dataset

### How Data Merging Works

The merging of parliament members (MPs) and government ministers is a key aspect of the pipeline:

1. **Politician Identity Management**: 
   - Each politician gets a unique identifier (`ui`)
   - Politicians who served as both MPs and ministers maintain the same `ui` across all roles
   - This allows tracking individuals across different positions and electoral terms

2. **Multiple Roles Handling**:
   - Each role for a person gets its own row in the final dataset
   - A politician can appear multiple times with the same `ui` but different roles
   - For example, Angela Merkel would have entries as an MP and additional entries as Chancellor

3. **Matching Process**:
   - Government members are matched to existing MPs by name and birth date
   - When matches are found, the government position is added while preserving the MP's `ui`
   - New entries are created for government members with no MP match

This approach ensures comprehensive coverage of all politicians while maintaining the relationships between their different roles and positions.

The serialization of intermediate results as pickle files enables efficient processing of the large dataset and supports the modular pipeline structure.

## Commands

- To setup the python environment, please run `make install-dev`
- To build the open-discourse data, please run `make full-run`

## Open Issues

Below is a comprehensive list of open issues in our fork of the Open Discourse project. These issues cover bug reports, feature requests, and refactoring tasks that need attention.

### Bug Reports

1. **[Issue #55](https://github.com/pmayd/open-discourse/issues/55): Wrong start date for electoral term 20**
   - In `create_electoral_terms.py` the electoral term 19 ends on 2021-10-26 and term 20 starts on 2021-10-27
   - This is incorrect as term 20 starts with its 1st session on 2021-10-26
   - The previous term should end on 2021-10-25

2. **[Issue #25](https://github.com/pmayd/open-discourse/issues/25): Names of MP (MdB) with accents are sometimes misspelled**
   - MPs with accented characters in their names have spelling inconsistencies
   - Affects searchability and data integrity

3. **[Issue #24](https://github.com/pmayd/open-discourse/issues/24): Incorrect and invalid characters from OCR recognition**
   - XML files from Deutscher Bundestag contain incorrect characters from OCR errors
   - These aren't fully corrected by the current cleaning process
   - Needs decision on approach: individual replacements, spell checkers, or other options

4. **[Issue #21](https://github.com/pmayd/open-discourse/issues/21): Name changes of MP (MdB) are not considered**
   - When MPs change their names (e.g., after marriage), the change isn't reflected in the data structure
   - Example: MP ID 11003569 Kristina Köhler changed to Kristina Schröder in 2010
   - This is in MDB_STAMMDATEN.XML but not mapped in the data structure

5. **[Issue #15](https://github.com/pmayd/open-discourse/issues/15): Link to protocol PDF constructed incorrectly for session numbers below 100 in term 20**
   - URLs to session protocols are malformed for certain session numbers
   - Affects accessibility of original documents

6. **[Issue #7](https://github.com/pmayd/open-discourse/issues/7): Function clean discards ending ("Schluß der Sitzung")**
   - The cleaning function removes the session ending text
   - Important metadata about session conclusion is being lost

7. **[Issue #6](https://github.com/pmayd/open-discourse/issues/6): Fix errors in extracting session content for script 02/02**
   - Issues with the extraction of session content in specific scripts
   - Needs investigation and correction

8. **[Issue #4](https://github.com/pmayd/open-discourse/issues/4): Start of indirect speech is wrongfully mislabeled as speaker entity**
   - Similar to original issue #104, but with specific focus
   - Indirect speech formatting is causing incorrect speaker attribution

9. **[Issue #3](https://github.com/pmayd/open-discourse/issues/3): Cleaning hyphenation at line breaks leads to formatting issues**
   - The process of fixing hyphenated words across line breaks is causing problems
   - Results in unrecognized speaker entities and other formatting issues

### Refactoring Tasks

10. **[Issue #27](https://github.com/pmayd/open-discourse/issues/27): Refactor 03_01_create_factions**
    - Need to modernize and improve the factions creation script
    - Part of ongoing code structure improvements

11. **[Issue #22](https://github.com/pmayd/open-discourse/issues/22): Refactor 05_create_electoral_terms.py**
    - Restructure the electoral terms creation script
    - Improve code quality and maintainability

12. **[Issue #19](https://github.com/pmayd/open-discourse/issues/19): Refactor 04_extract_mps_from_mp_base_data**
    - Improve the MP data extraction process
    - Enhance code structure and readability

13. **[Issue #12](https://github.com/pmayd/open-discourse/issues/12): Refactor 03_split_xml_electoral_term_20.py**
    - Modernize the XML splitting code for electoral term 20
    - Make the code more maintainable and efficient

14. **[Issue #8](https://github.com/pmayd/open-discourse/issues/8): Refactor 02_preprocessing/01_split_xml.py**
    - Improve the main XML splitting script
    - Part of general preprocessing improvement effort

### Feature Requests and Enhancements

15. **[Issue #36](https://github.com/pmayd/open-discourse/issues/36): Data checks: Analyze special chars in text-corpus**
    - Need for systematic analysis of special characters in text
    - Identify patterns of OCR errors or other character issues

16. **[Issue #14](https://github.com/pmayd/open-discourse/issues/14): Match OpenDiscourse politician IDs to Abgeordnetenwatch politician IDs**
    - Connect data with Abgeordnetenwatch platform (~1000 current and former members)
    - 90% of matches can be done automatically by first name, last name, and birth year
    - Remaining matches need fuzzy matching or manual verification

17. **[Issue #2](https://github.com/pmayd/open-discourse/issues/2): Investigate hyperscan library for faster regex matching**
    - Research using Intel's Hyperscan library for improved performance
    - Could dramatically speed up text processing operations

18. **[Issue #1](https://github.com/pmayd/open-discourse/issues/1): Update README**
    - Improve documentation for installation and usage
    - Update to use Makefile instead of previous scripts
    - Currently being addressed with ongoing documentation work

### Mirrors of Original Repository Issues

Several issues are mirrors of ones from the original repository, requiring local implementation:

- **[Issue #35](https://github.com/pmayd/open-discourse/issues/35)**: Original improvement #49 - Add Wikidata item to politicians
- **[Issue #34](https://github.com/pmayd/open-discourse/issues/34)**: Original improvement #54 - Progress logs in pipeline
- **[Issue #33](https://github.com/pmayd/open-discourse/issues/33)**: Original improvement #58 - Replace Contributions Placeholder
- **[Issue #32](https://github.com/pmayd/open-discourse/issues/32)**: Original bug report #63 - Slow search
- **[Issue #31](https://github.com/pmayd/open-discourse/issues/31)**: Original feature request #80 - Extend Search Functionality
- **[Issue #30](https://github.com/pmayd/open-discourse/issues/30)**: Original issue #81 - Fragestunden missing
- **[Issue #29](https://github.com/pmayd/open-discourse/issues/29)**: Original issue #104 - Wrong speaker assignment
- **[Issue #28](https://github.com/pmayd/open-discourse/issues/28)**: Original issue #115 - Spoken content matching

**Note**: If you are on Windows and have trouble installing `make`, I recommend you look into [Chocolatey](https://chocolatey.org/install) and then run `choco install make` or you directly use [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install), which I strongly recommend anyways, as it gives you full Linux OS under Windows that integrates smoothly with Windows. If you do not want to install additional programs, you can also directly inspect the [Makefile](./Makefile) and look up the commands that are execute for a given `make` command and run everything manually.

## Setup

1. This project uses [uv](https://docs.astral.sh/uv/). Please follow the install instructions according to your operating system. That's it, you are ready to use the Makefile!
2. Run `make install-dev` to install all required and dev dependencies into your virtual environment.
3. You are done! From now on you can always use `source .venv/bin/activate` to switch into the virtual environment or directly use `uv run ...` to run any command inside the environment (without the need to switch first into it).

**Note**: You should be inside the python folder, if you run `uv` or other commands, not in the root folder, so make sure to run `cd python` before doing anything else.

## Developing cycle

I will try to describe the general steps you should follow to start contributing.

1. Always make sure your `main` branch is up-to-date by running `git switch main && git pull`.
2. Create a new branch and give it a speaking name, ideally beginning with an issue number from our board: `git switch -c <branch-name>`.
3. Do your changes
4. If you need a new package, add id with `uv add <package>` or `uv add <package> --dev`, depending on whether it is a required package or a package used only during development.
5. Once you are done with your changes, add `pytest` unit tests for your functions and, if possible or applicable, add quality assurance tests to the `tests/qa` folder. Execute your tests with `uv run pytest tests`. **Warning**: Tests are not yet part of the pipeline!
6. If applicable, compare your refactoring changes to the previous version. You can switch to the branch `original-main`, which is the state of the project before we forked it and changed the logic, so it is up-to-date with the original repo. Run both pipelines up to your changed script and make sure that the output data files are identical.
7. You can and should open a PR as soon as possible to give others a chance to comment or get early feedback. Just push your branch with `git push` (when doing this for the first time, you also have to set up the upstream branch, just follow the command line instructions).
8. This will likeliy lead to a failing ci pipeline on GitHub and that is ok! Don't worry. To actually make the pipeline green, you should also run `make lint` and `make format`, which is identical to run `uv run ruff check --fix` and `uv run ruff format`. This will lint and format your project (make sure your code follows best practices and community style guides).
9. Another reason why the pipeline fails or the PR cannot be merged is that the main branch was updated in the meantime. You should make sure that you have the latest changes in your branch so run `git switch main && git pull && git switch <your-branch> && git merge main`. This will update the main branch and merge the latest changes in your branch.
