#!/usr/bin/env python3
"""
A script for unlinking all submodules and extracting their files.
"""

import logging

# Local logger
logger = logging.getLogger(__name__)

import os
import subprocess
import argparse
import logging
import shlex
import shutil
from pathlib import Path

def run_cmd(args : str, apply_change : bool = True, check : bool = True):
    """
    Runs a command

    :param args: The command as a string
    :param apply_change: Whether to apply the command or just log the execution of it
    :param check: Whether to check for errors or not
    """

    shlex_args = shlex.split(args)

    if not apply_change:
        logger.debug(f"[dry-run] {' '.join(shlex_args)}")
        return

    logger.debug(' '.join(shlex_args))
    subprocess.run(shlex_args, check = check)

def get_submodules():
    """
    Get all submodules

    :returns: List of all submodules
    """

    logger.info("Getting submodules.")

    gitmodules = Path('.gitmodules')
    if not gitmodules.exists():
        return []

    lines = gitmodules.read_text().splitlines()
    submodules = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('path = '):
            module = stripped_line.split(' = ', 1)[1].strip()
            logger.debug(f"Found submodule '{module}'.")
            submodules.append(module)
    return submodules

def remove_submodule_link(path: str, apply_change: bool):
    """
    Removes a linked submodule and its git meta data, but keeps all other files

    :param path: Submodule path
    :param apply_change: Whether to perform the removal or just log the execution of it
    """

    logger.info(f"Removing submodule '{path}'.")
    run_cmd(f'git rm --cached {path}', apply_change)
    run_cmd(f'git config --remove-section submodule.{path}', apply_change, check = False)

    dot_git = Path(f"{path}/.git")
    if dot_git.exists():
        if dot_git.is_dir():
            if apply_change:
                shutil.rmtree(dot_git)
            else:
                logger.debug(f"[dry-run] Removing {dot_git} directory.")
        else:
            if apply_change:
                dot_git.unlink()
            else:
                logger.debug(f"[dry-run] Removing {dot_git} file.")

    run_cmd(f'git add {path}')

def cleanup_gitmodules(apply_change: bool):
    """
    Removing .gitmodules if exists

    :param apply_change: Whether to perform the removal or just log the execution of it
    """

    gitmodules = Path('.gitmodules')
    if gitmodules.exists():
        run_cmd(f'git rm {gitmodules}', apply_change)

def ensure_repo_root():
    """
    Moves to the root of the Git repository
    """

    repo_root = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output = True, text = True, check = True
    ).stdout.strip()
    logger.debug(f"Moving to path {repo_root}.")
    os.chdir(repo_root)

def main():
    parser = argparse.ArgumentParser(
        description = "Extract Git submodules by removing links and keeping contents. Does not "
        "perform any changes unless called with --apply.")
    parser.add_argument('--apply', action = 'store_true', help = 'Apply actions.')
    parser.add_argument('--verbose', '-v', action = 'store_true', help = 'Enable debug logging.')
    args = parser.parse_args()

    logging.basicConfig(
        level = logging.DEBUG if args.verbose else logging.INFO,
        format = '[%(levelname)s] %(message)s'
    )

    ensure_repo_root()

    logger.info("Initializing submodules.")
    run_cmd('git submodule update --init --recursive', args.apply)

    submodules = get_submodules()
    if not submodules:
        logger.info("No submodules found.")
        return

    for submodule in submodules:
        remove_submodule_link(submodule, args.apply)

    cleanup_gitmodules(args.apply)

    logger.info("Done.")

if __name__ == "__main__":
    main()
