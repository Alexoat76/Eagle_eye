#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author:         Alex Arévalo (Alexoat76)

Module Name:    eagle_eye_streams.py

Description:    This Python module is an essential component of the Eagle Eye project,
                designed for extracting comprehensive information of Live Streams Section
                for any YouTube channels. It offers a clean and intuitive interface for
                efficient data scraping, ensuring a seamless experience for users.

Features:       - Quick and reliable data retrieval from YouTube channels.
                - Flexibility to scrape data form live streams section.
                - A progress bar to visualize the scraping progress.
                - Supports for saving data in multiple formats (CSV, TXT, XLSX, JSON)
                - Exception handling and error reporting to ensure a smooth scraping
                  experience.
                - Easy integration with other Python projects.
                - Clean and Maintainable code, with proper commenting and
                  documentation.

Dependencies:   This module is built on top of the following libraries:
                - python (3.10.12): To run the Python scripts
                - beautifulSoup (4.12.2): To parse the HTML
                - selenium (4.13.0): To automate the browser actions
                - lxml (4.9.3): To parse the HTML page source
                - json: To work with JSON files
                - pandas (2.1.1): To work with DataFrames
                - openpyxl (3.1.2): To work with Excel files
                - re: To work with regular expressions
                - time: To work with time series files
                - tqdm (4.66.1): To display a dynamic progress bar
                - typing: To use type hints
                - colorama (0.4.6): For enhancing the CLI with colored output
                - webdriver_manager (4.0.1): To manage the ChromeDriver binaries in the cache

Usage:          This module can be used in the following ways:
                - Integrate this module into your projects by importing and utilizing
                  its scraping functions.
                - Handle the scraped data in your preferred way, from data analysis
                  to reporting.

Version:        1.7 (Beta) - December 06, 2023
Copyright:      © 2023 - Alex Arévalo
License:        MIT License
"""
##############################################################################

# Import the required libraries and modules from the eagle_eye project

import datetime  # To work with dates and times
import json  # To work with JSON files
import pandas as pd  # To work with DataFrames
import time  # To work with time series files
import os  # To work with files and folders in the operating system
from time import sleep  # To sleep the execution of the program
import typing  # To work with types
from eagle_eye_utils import format_number  # To format the number.

# Import necessary libraries for Progressbar
from tqdm import tqdm  # To create a progress bar
from colorama import Fore  # To create a progress bar with color

# Import necessary libraries for Web Scraping
from bs4 import BeautifulSoup  # To parse the HTML page source
from selenium import webdriver  # To automate the browser actions

# Starting/Stopping the ChromeDriver and managing the ChromeDriver binaries
from selenium.webdriver.chrome.service import Service as ChromeService

# Allows searchs similar to bs4: find_all, find, select_one, select
from selenium.webdriver.common.by import By

# Manages the ChromeDriver binaries in the cache
from webdriver_manager.chrome import ChromeDriverManager

##############################################################################

# Constants
SCROLL_PAUSE = 0.5  # The amount of time to wait to load more content
MAX_SCROLLS = 100  # The maximum number of times to scroll the page
SCROLL_AMOUNT = 1000  # The amount to scroll in pixels

# Constants for color settings
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"

##############################################################################

def scroll_down_to_load(driver: ChromeDriverManager) -> None:
    """
    Scroll down to load more content.
    
    Args:
        driver (ChromeDriverManager): The Chrome WebDriver.
    """
    scroll_count = 0
    while True:
        driver.execute_script(f"scrollBy(0, {SCROLL_AMOUNT});")
        scroll_count += 1
        time.sleep(SCROLL_PAUSE)

        # Check if we've scrolled enough or reached the maximum scroll count
        if scroll_count >= MAX_SCROLLS:
            break

def setup_webdriver() -> ChromeDriverManager:
    """
    Set up the Chrome WebDriver.

    Returns:
        ChromeDriverManager: The Chrome WebDriver.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")  # Use incognito mode
    options.add_argument("--force-dark-mode")  # Use dark mode
    options.add_argument("--start-maximized")  # Maximize the browser window

    # Consider this if the application works and you know how it works for speed ups and rendering!
    options.add_argument('--headless=chrome')  # Run the browser in headless mode
    
    # Set the language of the browser to English
    options.add_argument('--lang=en');
    prefs = {"translate_whitelists": {"es":"en"},"translate":{"enabled":"true"}}
    options.add_experimental_option("prefs", prefs)

    # Install and configure the Chrome WebDriver using WebDriver Manager
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    return driver

def scrape_channel(input_value: str, max_videos: typing.Optional[int] = None) -> typing.List[str]:
    """
    Scrape the YouTube channel.

    Args:
        input_value (str): The YouTube channel username or id to scrape.
        max_videos (typing.Optional[int]): The maximum number of videos to scrape.

    Returns:
        typing.List[str]: The scraped data.
    """
    # Initialize the variables for the scraped data
    video_data = []

    if len(input_value) == 24 and input_value.isalnum():
        # Used to scrape data if the user enters the YouTube channel id
        url = f'https://www.youtube.com/channel/{input_value}/streams'
    else:
        # Used to scrape data if the user enters the YouTube channel name
        url = f'https://www.youtube.com/{input_value}/streams'

    print(f"Using URL: {GREEN}{url}{RESET}\n")  # Message for debugging purposes only

    try:
        driver = setup_webdriver()
        driver.get(url)  # Use the URL to navigate to the page
        time.sleep(3)  # Wait for 3 seconds for the page to load
        scroll_down_to_load(driver)  # Scroll down to load more content

        content = driver.page_source.encode('utf-8').strip()

        # Start the process of searching and extracting data from the YouTube channel.
        soup = BeautifulSoup(content, "lxml")  # Parse the page source with BeautifulSoup syntax

        # Find the channel name (username) for YouTube channel
        cname = soup.find('yt-formatted-string', id='channel-handle').text.strip()

        # Find the channel id for YouTube channel
        channel_ids = soup.find('meta', itemprop='identifier')['content']

        # Find the number of subscribers the channel has
        subscribers = soup.find('yt-formatted-string', id='subscriber-count').text.strip().split(' ')[0]

        # Find the description of the YouTube channel
        description = soup.find('meta', property='og:description')['content'].replace('\n', ' ').replace(',', ';')

        # Find the keywords for the YouTube channel
        keywords_elements = soup.findAll('meta', property='og:video:tag')
        keywords = []
        for element in keywords_elements:
            keyword = element['content']
            keywords.append(keyword)
        
        # Find all video live streams titles on the YouTube channel
        titles = soup.findAll('a', id='video-title-link')

        # Find how long ago the video live streams was uploaded
        uploads = soup.findAll('span', class_='inline-metadata-item style-scope ytd-video-meta-block')  # Find how long ago the video was uploaded
        
        # Find out how many views the video live streams has had
        counts = soup.findAll('span', class_='inline-metadata-item style-scope ytd-video-meta-block')  # Find out how many views the video has had
        
        # Find the id of the video live streams on YouTube
        video_ids = soup.findAll('a', id='video-title-link', href=True)  # Find the id of the video
        
        # Find the link to the video live streams on YouTube
        video_links = soup.findAll('a', id='video-title-link', href=True)  # Find the link to the video
        
        # Find the length of the video live streams in minutes and seconds
        terms = soup.findAll('span', class_='style-scope ytd-thumbnail-overlay-time-status-renderer')  # Find the length of the video in minutes and seconds

        # Count the number of videos scraped.
        total = len(titles)

        # Define a custom color for the progress bar
        custom_colors = {
            'GREEN': Fore.GREEN,
            'YELLOW': Fore.YELLOW,
            'BLUE': Fore.BLUE,
            'RED': Fore.RED,
            'WHITE': Fore.WHITE
            }
        # Select the color for the progress bar
        selected_color = custom_colors['GREEN']

        # Define the format of the progress bar with the selected color
        tqdm_bar_format = f"{{l_bar}}{selected_color}{{bar}}{Fore.RESET}{{r_bar}}"

        # Add a tqdm progress bar to visualize the scraping progress.
        # Loop through the total number of videos scraped.
        for i in tqdm(range(total), desc=f"Scraping {input_value} channel", unit="video", bar_format=tqdm_bar_format):
            if max_videos is not None and i >= max_videos:
                break  # Exit the loop when we've reached the maximum videos
            sleep(0.1)  # Sleep the execution of the program for 0.1 seconds
            cname = cname  # Name of the channel to scrape.
            channel_id = channel_ids  # ID of the channel to scrape.
            subscriber = subscribers  # Number of subscribers the channel has.
            description = description  # Description of the channel.
            keyword = keywords  # Keywords for YouTube channel.
            title = titles[i].text  # Title of the video on YouTube.
            published = uploads[1::2][i].text  # Time since the video was uploaded.
            counter = counts[0::2][i].text  # Number of views the video has had.
            counter_view = counter.split(' ')[0]
            view = format_number(counter_view)
            video_id = video_ids[i]['href'].split('=')[-1]  # ID of the video on YouTube.
            link = video_links[i]  # Link to the video on YouTube.
            term = terms[0::2][i].text.strip()  # Duration of the video in minutes and seconds.

            # Store the video info in a variable.
            #full_info = f"{cname}\t{channel_id}\t{subscriber}\t{joined}\t{location}\t{global_views}\t{description}\t{keyword}\t{title}\t{published}\t{view}\t{video_id}\thttps://www.youtube.com{link['href']}\t{term}"
            video_info = f"{cname}\t{channel_id}\t{title}\t{published}\t{view}\t{video_id}\thttps://www.youtube.com{link['href']}\t{term}"
            # Append the video info to the list.
            video_data.append(video_info.split('\t'))

        # Print the number of live streams scraped from the channel
        print(f"{GREEN}\n{input_value} channel has:{RESET} {YELLOW}{len(titles)} streams{RESET}.\n")

        # Check if the 'downloads' directory exists, if not, create it
        downloads_dir = 'downloads'
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        channel_folder = os.path.join(downloads_dir, cname)
        os.makedirs(channel_folder, exist_ok=True)

        # Get the current date and time from the system time zone
        current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save the information to a TXT file.
        txt_file_path = os.path.join(channel_folder, f"{cname}_streams_{current_datetime}.txt")
        with open(txt_file_path, "w", encoding='utf-8') as f:
            f.write("Channel\tIdentifier\tTitle\tPublished\tVideo_views\tVideo_id\tLink\tDuration\n")
            for video_info in video_data:
                f.write('\t'.join(video_info) + "\n")

        # Save the information to a CSV file.
        csv_file_path = os.path.join(channel_folder, f"{cname}_streams_{current_datetime}.csv")
        df = pd.DataFrame(video_data, columns=['Channel', 'Identifier', 'Title', 'Published', 'Video_views', 'Video_id', 'Link', 'Duration'])
        df.to_csv(csv_file_path, index=False, encoding='utf-8')

        # Save the information to a XLSX file.
        xlsx_file_path = os.path.join(channel_folder, f"{cname}_streams_{current_datetime}.xlsx")
        df.to_excel(xlsx_file_path, index=False)

        # Save the information to a JSON file.
        json_file_path = os.path.join(channel_folder, f"{cname}_streams_{current_datetime}.json")
        with open(json_file_path, "w", encoding='utf-8') as f:
            f.write(json.dumps(json.loads(df.to_json(orient='records')), indent=4, ensure_ascii=False))
        
    except Exception as e:
        print(f"An error occurred while scraping {input_value}: {e}")
    finally:
        if driver:
            driver.quit()

    return video_data

# End of file
