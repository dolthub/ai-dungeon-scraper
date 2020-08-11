#!/usr/bin/python3

import argparse
import re
import uuid 

from time import sleep

from doltpy.core import Dolt
from mysql.connector import connect
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException



def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape play.aidungeon.com. "
        "Must provide username and password. "
        "Once logged in, follow the prompts."
        )
    parser.add_argument('--email', help='Your email used to login')
    parser.add_argument('--password', help='Your password used to login.')
    args = parser.parse_args()
    return args

def is_logged_in(driver):
    driver.get('https://play.aidungeon.io/')
    sleep(1)

    try:
        login_button = driver.find_element_by_xpath("//div[@aria-label='Login']")
        return False
    except NoSuchElementException:
        return True
    

def login(driver, user, password):
    if is_logged_in(driver):
        return
    
    driver.get('https://play.aidungeon.io/')
    sleep(1)
    
    # Login to AI Dungeon
    login_button = driver.find_element_by_xpath("//div[@aria-label='Login']")
    login_button.click();
    sleep(1)

    email_input = driver.find_element_by_xpath("//input[@placeholder='Email']")
    email_input.send_keys(user)

    password_input = driver.find_element_by_xpath("//input[@placeholder='Password']")
    password_input.send_keys(password)

    login_buttons = driver.find_elements_by_xpath("//div[@aria-label='Login']")
    login_buttons[1].click();
    sleep(3)

    # Sometimes a splash screen apperas here. Try to handle. Need to test more
    try:
        enter_button = driver.find_element_by_xpath("//div[@aria-label='Enter']")
        enter_button.click()
    except NoSuchElementException:
        return

def collect_settings_info(driver):
    settings = {}
    
    # Go To Settings
    hamburger = driver.find_element_by_xpath("//div[@aria-label='Open Menu']")
    hamburger.click()
    sleep(1)

    settings_link = driver.find_element_by_xpath("//div[@aria-label='Settings']")
    settings_link.click()
    sleep(1)

    # Collect Settings Information

    # Dragon or Griffin
    ai_mode = ''
    if ( driver.find_element_by_xpath("//div[@aria-label='Dragon (selected)']") ):
        ai_mode='dragon'
    elif ( driver.find_element_by_xpath("//div[@aria-label='Dragon (selected)']") ):
        ai_mode='griffin'
    else:
        print("We done fucked up")
        exit
    
    settings['ai_mode'] = ai_mode

    randomness_el = driver.find_element_by_xpath("//div[contains(text(), 'Randomness')]")
    reg = 'Randomness:\s([\d\.]+).*'
    randomness = re.findall(reg, randomness_el.text)[0]
    settings['randomness'] = randomness
    
    length_el = driver.find_element_by_xpath("//div[contains(text(), 'Length')]")
    reg = 'Length:\s([\d]+).*'
    length = re.findall(reg, length_el.text)[0]
    settings['length'] = length

    direct_dialog = driver.find_element_by_xpath("//input[@aria-label='Direct Dialog']")
    settings['direct_dialog'] = direct_dialog.is_selected()

    # Close Settings Menu
    cancel_link = driver.find_element_by_xpath("//div[@aria-label='Cancel']")
    cancel_link.click()
    sleep(1)

    return settings

def play_session(driver, session, retries):
    # Start New Session
    new_game_link = driver.find_element_by_xpath("//div[@aria-label='New Singleplayer Game']")
    new_game_link.click()
    sleep(2)

    # Pick a setting
    # Will default to custom now (#6 in current menu)
    textarea = driver.find_element_by_xpath("//textarea")
    textarea.send_keys("6")
    submit_button = driver.find_element_by_xpath("//div[@aria-label='Submit']")
    submit_button.click()
    sleep(3)

    session['setting'] = 'custom'

    # Somehow there are two textareas. Taking the second one works.
    textareas = driver.find_elements_by_xpath("//textarea[@aria-label='...']")

    session['prs'] = []
    while (1):
        prompt = input("Enter your prompt. Enter 'exit' to exit:\n")
        if (prompt == 'exit'):
            return
        else:
            print("Please wait for reply...")
    
            pr = prompt_response(driver, textareas[1], prompt, retries)
            print(pr['response'][-1])
            session['prs'].append(pr)

def get_session_id():
    return str(uuid.uuid1())

def prompt_response(driver, textarea, prompt, retries):
    prompt_response = {}

    # Get the prompt type. Should be "story" for now.
    prompt_type = get_prompt_type(driver)

    prompt_response['prompt'] = prompt
    prompt_response['prompt_type'] = prompt_type
    
    textarea.send_keys(prompt)
    textarea.send_keys(Keys.RETURN)
    sleep(10)

    # Grab the response.
    spans = driver.find_elements_by_xpath("//span")

    prompt_response['response'] = []
        
    prompt_response['response'].append(get_response(prompt, spans))

    # Retries Disabled.
    if retries > 0:
        retry_buttons = driver.find_elements_by_xpath(
            "//div[@aria-label='retry']"
        )
        for i in range(0, retries):
            retry_buttons[1].click()
            sleep(10)
            
            prompt_response['response'].append(get_response(prompt, spans))

    return prompt_response

def get_response(prompt, spans):
    i = 0
    response = ''
    recording = 0
    match = re.search(prompt, spans[i].text)
    while i < len(spans):
        if ( recording == 1 ):
            response += spans[i].text
        elif ( prompt in spans[i].text ):
            recording = 1
            
        i += 1
        
    return response

def get_prompt_type(driver):
    # This is pretty ugly
    try:
        driver.find_element_by_xpath("//div[@aria-label='Story']")
        return "story"
    except NoSuchElementException:
        try:
            driver.find_element_by_xpath("//div[@aria-label='Do']")
            return "do"
        except NoSuchElementException:
            try:
                driver.find_element_by_xpath("//div[@aria-label='Say']")
                return 'say'
            except NoSuchElementException:
                return ''

def write_to_dolt():
    repo = Dolt.clone("Liquidata/ai-dungeon", "/tmp/ai-dungeon/")

    
            
def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")

    args = parse_args()    

    driver = webdriver.Chrome(executable_path="/Users/timsehn/liquidata/dolt/ai-dungeon/chromedriver", options=chrome_options)

    session  = {}

    session['user'] = args.email

    print("Logging into AI Dungeon")
    login(driver, args.email, args.password)
    session['id'] = get_session_id()

    print("Collecting Settings Information.")
    session['settings'] = collect_settings_info(driver)

    num_retries = 0
    
    print("Starting Session.")
    play_session(driver, session, num_retries)
    print(session)

    write_to_dolt()
    
    # driver.close()

main()
