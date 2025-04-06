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

## Visual Progress Tracking

The pipeline now includes a visual progress tracker that updates the ExecutionGraph image as tasks complete. This helps you:

- Visualize which steps in the pipeline have completed
- See which step is currently executing
- Understand the overall progress through the data processing workflow

### Using the Progress Tracker

The progress tracking is automatically enabled when you run tasks through doit:

```bash
# Run the entire pipeline with progress tracking
uv run doit

# Run a specific group of tasks
uv run doit 04_politicians

# View the current progress at any time
uv run doit show_progress
```

As tasks run, the ExecutionGraph_progress.png file will be updated showing:
- Green boxes with checkmarks for completed tasks
- Yellow boxes for currently running tasks
- Original colors for pending tasks

### Demo the Progress Tracker

To see the progress tracker in action without running the actual tasks:

```bash
uv run python demo_progress_tracker.py
```

This will simulate the pipeline execution and show the visual progress updates.

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
