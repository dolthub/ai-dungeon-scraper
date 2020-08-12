# ai-dungeon-scraper

This is an interactive python script to scrape AI Dungeon and place the prompt response pairs in the [ai-dungeon Dolt repository](https://www.dolthub.com/repositories/Liquidata/ai-dungeon). The goal is to create an open dataset of prompt response pairs. If you have a paid membership to AI Dungeon and set the mode to Dragon, you will get GPT-3 responses.

# Installation.

1. Clone this repository.
2. Install the dependencies
    1. [Install Dolt](https://www.dolthub.com/docs/tutorials/installation/)
    1. pip3 install selenium
    2. pip3 install doltpy
    3. [Install the chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) in the directory where the scraper lives.

# Use

Run the scraper and pass in the `--email` and `--password` used to log in to AI Dungeon. Enter prompts and view responses. Once you exit, the script will clone the AI Dungeon Dolt repository and insert the new information. It is up to you whether to commit or not.
