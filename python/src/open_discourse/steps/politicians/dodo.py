"""
Task definitions for the politicians processing steps.

This module defines doit tasks for processing politicians data:
1. scrape_mgs: Scrape Wikipedia for government members
2. add_faction_id_to_mps: Add faction IDs to parliamentarians
3. merge_politicians: Merge parliamentarians and government members data
"""

import os
from pathlib import Path

from open_discourse.definitions import path
from open_discourse.steps.politicians.scrape_mgs import main as scrape_mgs_main
from open_discourse.steps.politicians.add_faction_id_to_mps import main as add_faction_id_main
from open_discourse.steps.politicians.merge_politicians import main as merge_politicians_main


def task_scrape_mgs():
    """Scrape government members data from Wikipedia."""
    stage_01_dir = path.POLITICIANS_STAGE_01
    output_file = stage_01_dir / "mgs.pkl"
    
    return {
        'actions': [(scrape_mgs_main,)],
        'targets': [output_file],
        'uptodate': [False],  # Always run to check for updates
        'verbosity': 2,
    }


def task_add_faction_id_to_mps():
    """Add faction IDs to parliamentarians (MPs) data."""
    stage_01_dir = path.POLITICIANS_STAGE_01
    stage_02_dir = path.POLITICIANS_STAGE_02
    factions_dir = path.DATA_FINAL
    
    input_file = stage_01_dir / "mps.pkl"
    factions_file = factions_dir / "factions.pkl"
    output_file = stage_02_dir / "mps.pkl"
    
    return {
        'actions': [(add_faction_id_main,)],
        'file_dep': [input_file, factions_file],
        'targets': [output_file],
        'verbosity': 2,
    }


def task_merge_politicians():
    """Merge parliamentarians and government members data."""
    stage_01_dir = path.POLITICIANS_STAGE_01
    stage_02_dir = path.POLITICIANS_STAGE_02
    factions_dir = path.DATA_FINAL
    
    mps_file = stage_02_dir / "mps.pkl"
    mgs_file = stage_01_dir / "mgs.pkl"
    factions_file = factions_dir / "factions.pkl"
    output_file = factions_dir / "politicians.csv"
    
    return {
        'actions': [(merge_politicians_main,)],
        'file_dep': [mps_file, mgs_file, factions_file],
        'targets': [output_file],
        'verbosity': 2,
    }