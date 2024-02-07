#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author:         Alex Arévalo (Alexoat76)

Module Name:    eagle_eye_utils.py

Description:    This Python module contains the utility functions for the Eagle Eye.
                It is meant to be imported by the main module in the Eagle Eye project.
                
Features:       - Ctrl+C signal handler to exit the program.
                - Command-line arguments parser.
                - Getting the YouTube channel input from the user.
                
Dependencies:   This module is built on top of the following libraries or modules:
                - python (3.10.12): To run the Python scripts
                - argparse: To parse the command-line arguments
                - pandas (2.1.1): To work with DataFrames
                - signal: To handle the Ctrl+C signal (SIGINT)
                - sys: To exit the program (sys.exit)
                - typing: To use type hints

Usage:          This module can be used in the following ways:
                - Imports the utility functions of this module into the eagle_eye_main
                  module.

Version:        1.7 (Beta) - December 06, 2023
Copyright:      © 2023 - Alex Arévalo
License:        MIT License
"""

##############################################################################

# Import the required libraries
import argparse  # To parse the command-line arguments
import os  # To work with the operating system
import pandas as pd  # To work with pandas DataFrames
import signal  # To handle the Ctrl+C signal
import sys  # To exit the program
import typing # To use type hints

##############################################################################

# Constants for color settings
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"

##############################################################################

user_choice_info = None


# Function to print the program's version
def print_version() -> None:
    """
    Prints the program's version.

    Returns:
        The current version of the program.
    """
    print(f"{YELLOW}\nEagle Eye Project{RESET} {GREEN}Version 1.7 (Beta){RESET}")


# Function to parse the command-line arguments from the CLI
def parse_arguments() -> argparse.Namespace:
    """
    Parses the command-line arguments from the CLI.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Eagle Eye Project')
    parser.add_argument('channels', metavar='channel', type=str, nargs='*', help='The channel(s) to be analyzed')
    parser.add_argument('--version', '-v', '-V', action='store_true', help='Print the version of the project')
    return parser.parse_args()


# Function to get the YouTube channel input from the user
def get_channel_input() -> typing.List[str]:
    """
    Prompts the user to enter the YouTube channel username(s) to scrape.

    Returns:
        typing.List[str]: The YouTube channel username(s) to scrape.
    """
    while True:
        # Get the channel input from the user's channel
        channels_to_scrape = input(f"{YELLOW}\nEnter the YouTube channel username to scrape{RESET} ({GREEN}separated by commas{RESET}): {RESET}").split(',')
        channels_to_scrape = [channel.strip() for channel in channels_to_scrape if channel.strip()]
        if channels_to_scrape:
            return channels_to_scrape
        else:
            print(f"{RED}\nWARNING: No channel usernames provided. Please specify at least one channel to scrape.{RESET}")


# Function to get the data type to scrape
def get_data_type_to_scrape() -> str:
    """
    Prompts the user to select the data type to scrape.
    
    Returns:
        str: The data type to scrape (videos, streams, or shorts).
    """
    while True:
        # Define the text to be displayed to the user to select the data type
        input_text = (
            f"{YELLOW}\nPlease, choose what to scrape:\n\n" \
            "1) Videos\n" \
            "2) Streams\n" \
            "3) Shorts\n\n"
        )

        selection = input((input_text) + f"{GREEN}").strip()
        print(f"{RESET}")

        if selection == '1':
            return 'videos'
        elif selection == '2':
            return 'streams'
        elif selection == '3':
            return 'shorts'
        else:
            print(f"{RED}WARNING: Invalid selection. Please try again.{RESET}")


# Function to get the maximum number of videos to scrape
def get_max_videos_to_scrape() -> typing.Optional[int]:
    """
    Prompts the user to enter the maximum number of videos to scrape.

    Returns:
        typing.Optional[int]:   The maximum number of videos to scrape or None
                                if the user wants to scrape all videos.
    """
    while True:
        max_videos_input = input(f"{YELLOW}\nEnter the maximum number of videos to scrape{RESET} ({GREEN}or press Enter for all{RESET}): ")
        if not max_videos_input:
            return None  # No input provided, so return None for all videos
        try:
            max_videos = int(max_videos_input)
            if max_videos > 0:
                return max_videos  # Return the maximum number of videos to scrape
            else:
                print(f"{RED}\nWARNING: Please enter a positive number or press Enter for all.{RESET}")
        except ValueError:
            print(f"{RED}\nWARNING: Invalid input. Please enter a positive number or press Enter for all.{RESET}")


# Function to obtain the format in which the user wants to save the data
def get_format_selection() -> typing.List[str]:
    """
    Prompts the user to select the format in which to save the data.

    Returns:
        typing.List[str]:   The format(s) in which to save the data.
    """
    # Define the valid format options as a set of strings
    valid_formats = set(['1', '2', '3', '4', '5'])

    # Initialize an empty list to store the user's format selection
    format_selection = []

    while not format_selection:
        # Define the text to be displayed to the user to select the format
        input_text = (
            f"\nSelect the format of your choice to save the data:\n\n" \
            "1) CSV format\n" \
            "2) TXT format\n" \
            "3) XLSX format\n" \
            "4) JSON format\n" \
            "5) All available formats\n"
        )

        input_text = f"{YELLOW}" + input_text + f"{RESET}\n"
        format_selection = input((input_text) + f"{GREEN}").strip().split(',')
        print(f"{RESET}")

        # Check if the user's choices are valid format options
        if not all(choice in valid_formats for choice in format_selection):
            print(f"{RED}WARNING: Invalid format selection. Please try again.{RESET}")
            format_selection = []

    # Check if the user entered a valid format selection
    for choice in format_selection:
        if choice not in valid_formats:
            print(f"{RED}\nWARNING: Invalid format selection. Please try again.{RESET}")
            format_selection = []

    return format_selection


# Function to get the user's choice info to be scraped (video information or channel summary).
def get_user_choice_info() -> str:
    """
    Get the user's choice for the type of information to scrape.

    Returns:
        str: The user's choice (1 for video info, 2 for channel info).
    """
    global user_choice_info

    # Check if the user's choice has already been set
    if user_choice_info is not None:
        return user_choice_info

    while True:
        # Display a menu for the user to choose the type of information to scrape
        print(f"\n{YELLOW}What type of information would you like to scrape?{RESET}\n")
        print(f"{YELLOW}1) Video Info{RESET} {GREEN}(Detailed information for each video){RESET}")
        print(f"{YELLOW}2) Channel Info{RESET} {GREEN}(Summary information for the channel){RESET}\n")
        
        # Prompt the user for their choice_info
        prompt = f"{YELLOW}Enter the number of your choice:{RESET}"
        choice_info: str = input(f"{prompt} {GREEN}").strip()
        print(f"{RESET}")

        # Validate the user's choice
        if choice_info in ["1", "2"]:
            user_choice_info = choice_info
            return choice_info
        else:
            print(f"{RED}WARNING: Invalid choice. Please enter 1 or 2.{RESET}\n")


# Function to format the number in a concise way.
def format_number(number: str) -> str:
    """
    Format the number in a concise way (e.g., 1K for 1000, 1M for 1 million).

    Args:
        number (str): The number to be formatted.

    Returns:
        str: The formatted number.
    """
    try:
        # Define a mapping of suffixes to multipliers
        suffix_multiplier = {'K': 1_000, 'M': 1_000_000, 'k': 1_000, 'm': 1_000_000}

        # Extract the last character as the suffix
        suffix = number[-1]

        # Determine the multiplier based on the suffix
        multiplier = suffix_multiplier.get(suffix, 1)

        # Convert the part of the number without the suffix to a float
        num = float(number[:-1]) if suffix in suffix_multiplier else float(number)

        # Multiply the number by the multiplier
        num *= multiplier

        # Convert the number to an integer
        num = int(num)

        # Format the number with commas
        return f"{num:,}"
    except ValueError:
        # If the conversion to float fails, return the original number
        return number


# Function to merge summary files
def merge_summary_files(folder_path):
    """
    Merge summary files for all channels into a single file.

    Args:
        folder_path (str): The path to the folder containing summary files.
    """
    # Get all summary files in the folder.
    summary_files = [file for file in os.listdir(folder_path) if file.endswith("_summary.csv")]

    if not summary_files:
        print("No summary files found for merging.")
        return

    # Merge all summary files into a single DataFrame
    merged_df = pd.concat([pd.read_csv(os.path.join(folder_path, file)) for file in summary_files], ignore_index=True)

    # Save the summary information in the CSV format
    csv_path = os.path.join(folder_path, "summary_all_channels.csv")
    merged_df.to_csv(csv_path, index=False)

    # Save the summary information in the TXT format
    txt_path = os.path.join(folder_path, "summary_all_channels.txt")
    merged_df.to_csv(txt_path, index=False, sep='\t')

    # Save the summary information in the XLSX format
    xlsx_path = os.path.join(folder_path, "summary_all_channels.xlsx")
    merged_df.to_excel(xlsx_path, index=False)

    # Save the summary information in the JSON format
    json_path = os.path.join(folder_path, "summary_all_channels.json")
    merged_df.to_json(json_path, orient="records", indent=4)

    print(f"{GREEN}Summary files merged successfully.{RESET}")
    #{YELLOW}Merged file saved at:{RESET} {GREEN}{csv_path}{RESET}\n")

# Function to handle the Ctrl+C interrupt
def signal_handler(signal, frame):
    """
    Handles the Ctrl+C interrupt.

    Args:
        signal: The signal to handle.
        frame: The current stack frame.
    """
    # Print a warning message to the user and exit the program
    print(f"{RED}\n\nWARNING:{RESET} Ctrl+C detected. {YELLOW}Exiting the program ...{RESET}")
    # Add any cleanup code here if necessary
    sys.exit(0)

# Register the Ctrl+C signal handler
signal.signal(signal.SIGINT, signal_handler)
