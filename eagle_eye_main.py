#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author:         Alex Arévalo (Alexoat76)

Module Name:    eagle_eye_main.py

Description:    This Python module serves as the core component of the Eagle Eye project,
                allowing users to collect complete data from any YouTube channel,
                allowing to select between different sections, such as main videos,
                live streams and short videos. The program provides an easy-to-use
                interface for initiating and customizing data extraction tasks.

Features:       - Seamless integration with Eagle Eye's sub-modules for videos, streams, 
                  and shorts.
                - Interactive command-line interface for selecting channels and data types.
                - Customizable options for scraping any number of videos/streams.
                - Support for multiple data export formats (CSV, TXT, XLSX, JSON).
                - Effective Ctrl+C handling for clean program termination.
                - Clean and Maintainable code, with proper commenting and
                  documentation.

Dependencies:   This module is built on top of the following libraries or modules:
                - python (3.10.12): To run the Python scripts
                - pandas (2.1.1): To work with DataFrames
                - openpyxl (3.1.2): To work with Excel files
                - csv: To work with CSV files
                - json: To work with JSON files
                - eagle_eye_videos.py: To scrape videos from YouTube channels
                - eagle_eye_streams.py: To scrape streams from YouTube channels
                - eagle_eye_shorts.py: To scrape shorts from YouTube channels
                - eagle_eye_utils.py: To manage the utility functions of the Eagle Eye project

Usage:          This module can be used in the following ways:
                - Execute this script to initiate the data scraping process.
                - Follow on-screen prompts to specify the channels, data types,
                  and export formats.
                - Handle the scraped data according to your project's needs,
                  from analysis to reporting.

Version:        1.7 (Beta) - December 06, 2023
Copyright:      © 2023 - Alex Arévalo
License:        MIT License
"""
##############################################################################

# Import the required libraries and modules from the eagle_eye project
import eagle_eye_videos
import eagle_eye_streams
import eagle_eye_shorts
import eagle_eye_utils
import csv  # To work with CSV files
import json  # To work with JSON files
import pandas as pd  # To work with DataFrames
import datetime  # To work with dates and times
import os  # To work with the operating system

##############################################################################

# Constants for color settings
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"

##############################################################################

def main():
    # Parse the command-line arguments
    args = eagle_eye_utils.parse_arguments()

    if args.version:
        version = eagle_eye_utils.print_version()
        return

    if not args.channels:
        # Ask the user for the YouTube channel to scrape
        channels_to_scrape = eagle_eye_utils.get_channel_input()

        if not channels_to_scrape:
            return
    else:
        channels_to_scrape = args.channels

    # Ask the user for the type of data to scrape (videos/streams/shorts)
    selection = eagle_eye_utils.get_data_type_to_scrape()
    print(f"{GREEN}You selected to scrape:{RESET} {YELLOW}{selection}{RESET}")

    # Get the user's choice for the type of information to scrape
    if selection == 'videos':
        choice_info = eagle_eye_utils.get_user_choice_info()
    else:
        # For streams/shorts, default to 'Video Info' without asking the user
        choice_info = '1'

    # Ask the user for the maximum number of videos/streams/shots to scrape
    max_videos = eagle_eye_utils.get_max_videos_to_scrape()
    if max_videos is None:
        print(f"{GREEN}\nYou chose to scrape all data for your election.{RESET}")
    else:
        print(f"{GREEN}\nYou have chosen to scrape a maximum of{RESET} {YELLOW}{max_videos}{RESET} {GREEN}videos, streams or shorts according to your preference.{RESET}")

    # Ask the user for the format(s) to save the data
    format_selection = eagle_eye_utils.get_format_selection()

    # Print the selected format(s)
    if '5' in format_selection:
        print(f"{GREEN}You have chosen to save the data in the:{RESET} {YELLOW}all available formats.{RESET}")
    else:
        print(f"{GREEN}You selected the following format(s):{RESET}\n")
        for choice in format_selection:
            if choice == '1':
                print(f"{YELLOW}CSV format{RESET}")
            elif choice == '2':
                print(f"{YELLOW}TXT format{RESET}")
            elif choice == '3':
                print(f"{YELLOW}XLSX format{RESET}")
            elif choice == '4':
                print(f"{YELLOW}JSON format{RESET}")

    data = []  # To store the data of each video/stream/short

    # Check if the 'downloads' directory exists, if not, create it
    downloads_dir = 'downloads'
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)

    # Scrape the YouTube channel for videos/streams/shorts
    for channel in channels_to_scrape:
        if selection == 'videos':
            # Let the user know that the scraping has started
            print(f"{GREEN}\nPlease wait ...{RESET}\n")
            scraped_data = eagle_eye_videos.scrape_channel(channel.strip(), max_videos, choice_info)
        elif selection == 'streams':
            # Let the user know that the scraping has started
            print(f"{GREEN}\nPlease wait ...{RESET}\n")
            scraped_data = eagle_eye_streams.scrape_channel(channel.strip(), max_videos)
        elif selection == 'shorts':
            # Let the user know that the scraping has started
            print(f"{GREEN}\nPlease wait ...{RESET}\n")
            scraped_data = eagle_eye_shorts.scrape_channel(channel.strip(), max_videos)
        else:
            print(f"{RED}\nWARNING: Invalid selection. Please try again.{RESET}")

        if scraped_data is not None:
            data.extend(scraped_data)
            
    if data:
        if selection == 'shorts':
            # Create a DataFrame for shorts
            df = pd.DataFrame(data, columns=["Channel", "Identifier", "Title", "Video_views", "Video_id", "Link"])
        else:
            # Create a DataFrame for regular videos
            df = pd.DataFrame(data, columns=["Channel", "Identifier", "Title", "Published", "Video_views", "Video_id", "Link", "Duration"])

        # # Create a folder with all data scraped in the selected format for all the channels to scraped
        # channels_folder = os.path.join(downloads_dir, f"all_{selection}_channels")
        # os.makedirs(channels_folder, exist_ok=True)

        # Save the data in the selected format(s)
        if '5' in format_selection:
            saved_in_all_formats = False

            if choice_info == '1':
                # Create a folder with all data scraped in the selected format for all the channels to scraped
                channels_folder = os.path.join(downloads_dir, f"all_{selection}_channels")
                os.makedirs(channels_folder, exist_ok=True)
                
                # Get the current date and time from the system time zone
                current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

                for choice in ['1', '2', '3', '4']:
                    if choice == '1':
                        # Save the data to a CSV file
                        csv_file_path = os.path.join(channels_folder, f"all_{selection}_eagle_eye_{current_datetime}.csv")
                        with open(csv_file_path, "w", encoding="utf-8") as csv_file:
                            writer = csv.writer(csv_file)
                            # Write the header of the CSV file
                            writer.writerow(df.columns)
                            writer.writerows(data)
                        saved_in_all_formats = True
                    elif choice == '2':
                        # Save the data to a TXT file
                        txt_file_path = os.path.join(channels_folder, f"all_{selection}_eagle_eye_{current_datetime}.txt")
                        with open(txt_file_path, "w", encoding="utf-8") as txt_file:
                            # Write the header of the TXT file
                            txt_file.write('\t'.join(df.columns) + '\n')
                            for row in data:
                                # Write each row as a tab-separated line
                                txt_file.write('\t'.join(row) + '\n')
                        saved_in_all_formats = True
                    elif choice == '3':
                        # Save the data to an Excel file
                        xlsx_file_path = os.path.join(channels_folder, f"all_{selection}_eagle_eye_{current_datetime}.xlsx")
                        df.to_excel(xlsx_file_path, index=False)
                        saved_in_all_formats = True
                    elif choice == '4':
                        # Save the data to a JSON file
                        json_file_path = os.path.join(channels_folder, f"all_{selection}_eagle_eye_{current_datetime}.json")
                        with open(json_file_path, "w", encoding="utf-8") as f:
                            # Write the JSON data to a file with indentation
                            f.write(json.dumps(json.loads(df.to_json(orient="records")), indent=4, ensure_ascii=False))
                        saved_in_all_formats = True

            if saved_in_all_formats:
                print(f"{YELLOW}Data saved in All available formats.{RESET}")
        else:
            for choice in format_selection:
                if choice_info == '1':                   
                    if choice == '1':
                        # Save the data to a CSV file
                        csv_file_path = os.path.join(channels_folder, f"all_{selection}_eagle_eye_{current_datetime}.csv")
                        with open(csv_file_path, "w", encoding="utf-8") as csv_file:
                            writer = csv.writer(csv_file)
                            # Write the header of the CSV file
                            writer.writerow(df.columns)
                            writer.writerows(data)
                        print(f"{YELLOW}Data saved in CSV format.{RESET}")
                    elif choice == '2':
                        # Save the data to a TXT file
                        txt_file_path = os.path.join(channels_folder, f"all_{selection}_eagle_eye_{current_datetime}.txt")
                        with open(txt_file_path, "w", encoding="utf-8") as txt_file:
                            # Write the header of the TXT file
                            txt_file.write('\t'.join(df.columns) + '\n')
                            for row in data:
                                # Write each row as a tab-separated line
                                txt_file.write('\t'.join(row) + '\n')
                        print(f"{YELLOW}Data saved in TXT format.{RESET}")
                    elif choice == '3':
                        # Save the data to an Excel file
                        xlsx_file_path = os.path.join(channels_folder, f"all_{selection}_eagle_eye_{current_datetime}.xlsx")
                        df.to_excel(xlsx_file_path, index=False)
                        print(f"{YELLOW}Data saved in XLSX format.{RESET}")
                    elif choice == '4':
                        # Save the data to a JSON file
                        json_file_path = os.path.join(channels_folder, f"all_{selection}_eagle_eye_{current_datetime}.json")
                        with open(json_file_path, "w", encoding="utf-8") as f:
                            # Write the JSON data to a file with indentation
                            f.write(json.dumps(json.loads(df.to_json(orient="records")), indent=4, ensure_ascii=False))
                        print(f"{YELLOW}Data saved in JSON format.{RESET}")

        # Count the number of videos/streams scraped from all the channels
        total_scraped = len(data)

        # Print the total number of videos/streams scraped from all the channels
        print(f"{YELLOW}\nTotal number of {selection} scraped from all the channels: {RESET}{total_scraped}")
        print(f"{GREEN}\nScraping completed successfully!{RESET}")

    else:
        print(f"{RED}\nWARNING: No data was scraped. Please try again.{RESET}")


if __name__ == "__main__":
    main()

# End of file
# e.g.: channels_to_scrape = ["NetworkChuck", "JohnWatsonRooney"] NetworkChuck, JohnWatsonRooney