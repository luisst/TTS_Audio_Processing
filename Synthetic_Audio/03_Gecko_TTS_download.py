
'''/**************************************************************************
    File: ttsmp3_download_with_login.py
    Author(s): Mario Esparza, Luis Sanchez
    Date: 02/27/2021

    Automatically download audios from ttsmp3.com. Words to be downloaded will
    be chosen from AOLME's and TIMIT's vocabularies. In this program we use
    the 1 million characters version (requires a purchase).

    NOTE: There might be some words that throw off ttsMP3. They give error:
    "Your audio file was created but is corrupt. Please check your message for
    invalid characters". If this happens, use {avoid_words} below to add them
    to the list; this way it is avoided in future runs.
    
***************************************************************************''' 
import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import sys
import time
import pandas as pd
import os 


dir_path = os.path.dirname(os.path.realpath(__file__))

def obtain_phrases(input_folder, current_lang):
    lines = []
    for file in sorted(os.listdir(input_folder)):
        if file.endswith('_{}.txt'.format(current_lang)):
            file_path = input_folder + '/' + file
            print(file_path)
            with open('{}'.format(file_path)) as f:
                lines = [line.rstrip() for line in f]
    return lines

                

def check_folder(this_folder):
    #Make sure {this_folder} exists. If it does, ask if ok to continue
    if not os.path.isdir(this_folder):
        os.mkdir(this_folder)
        
    if len(os.listdir(this_folder)) != 0:
        print(f"\n{this_folder} isn't empty, c for continue or q for quit?")
        if input().lower() != 'c':
            sys.exit()

person = 'Justin' #['Mia', 'Miguel', 'Lupe', 'Penelope']
avoid_words = {'Mia': [], 'Miguel': [], 'Penelope': [], 'Lupe': [],
               'Joey': [], 'Ivy': [], 'Justin': []}
start = 0
end = 1083

tts_link = 'https://ttsmp3.com/login.php'
#Load credentials (saved as environmental variables)
usr = os.environ['TTS_USR']
psw = os.environ['TTS_PSW']
Login_Xpath = '/html/body/div[2]/form/input[3]'
#Folder where audios will be saved
folder_mp3 = dir_path + '/tts_' + person

check_folder(folder_mp3)

input_folder = dir_path + '/input_txts'
lang_list = ['english', 'spanish']

# find language idx based on the name of the file
# create a new utils functions to deal with file extraction
lang_idx = 0

vocabulary = obtain_phrases(input_folder, lang_list[lang_idx])

print(f"\nVocabulary is composed of {len(vocabulary)} words")

#If there are words that cause issues in TTSMP3, remove them from vocabulary
if len(avoid_words[person]) != 0:
    for idx, word in enumerate(vocabulary):
        if word in avoid_words[person]:
            print(f"- '{word}' has been removed from vocabulary")
            vocabulary.pop(idx)
            
    print("\nAfter removing 'avoid_words', vocabulary is composed of "
          f"{len(vocabulary)} words")

#Setup Firefox's settings so that it doesn't ask for download confirmation
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList",2)
fp.set_preference("browser.download.manager.showWhenStarting",False)
fp.set_preference("browser.download.dir", folder_mp3)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/mp3")

#Grab driver, open website and assert
driver = webdriver.Firefox(firefox_profile=fp)
driver.get(tts_link)
assert "ttsMP3" in driver.title

#Use credentials and login
username = driver.find_element_by_name('username')
username.send_keys(usr)
password = driver.find_element_by_name('password')
password.send_keys(psw)
login_button = driver.find_element_by_xpath(Login_Xpath)

#Ensure login button is in fact the login button since we are using xpath
if login_button.get_attribute('value') != ' Login ':
    driver.close()
    print("\033[33m" + "ERROR: " + "\033[0m", end='') #to print in red
    print("Assertion of login button failed, you may want to check its xpath")
    sys.exit()
    
login_button.click()
#Give time to login
time.sleep(7)

for word in vocabulary[start:end]:
    print(word)
    select = Select(driver.find_element_by_id("sprachwahl"))
    select.select_by_value(person)
    time.sleep( 1.5 ) #Give it time to select value
    text_area = driver.find_element_by_id("voicetext")
    text_area.send_keys(word)
    
    download_button = driver.find_element_by_id("downloadenbutton")
    download_button.click()
    time.sleep(6) #Give it time to download
    text_area.clear()

driver.close() #if you want to close tab, use driver.quit() instead

#Get list of downloaded audios
mp3_audios = sorted(os.listdir(folder_mp3))

#Access MP3 download folder and rename files (add leading zero to minutes, 
# seconds, hours, day and month)
for audio in mp3_audios:
    src = folder_mp3 + '/' + audio
    digits = audio.split('_VoiceText_')[1][:-4]
    year, month, others = digits.split('-')
    day, others = others.split('_')
    hour, minute, sec = others.split(' ')
    dst = folder_mp3 + '/'
    dst += 'ttsmp3' + year + '_' + month.zfill(2) + '_' + day.zfill(2) + '_'
    dst += hour.zfill(2) + '_' + minute.zfill(2) + '_' + sec.zfill(2) + '.mp3'
    os.rename(src, dst)
    
print(f"\nAll {len(mp3_audios)} mp3 audios have been renamed (leading zeros) "
      f"have been added. Ranging from {start} to {end}.")

#Rename files in download folder (implement a custom filename/ID)
mp3_audios = sorted(os.listdir(folder_mp3))
counter = 0
for word, audio in zip(vocabulary[start:end], mp3_audios):
    src = folder_mp3 + '/' + audio
    index = str(start + counter)
    dst = folder_mp3 + '/' + index.zfill(4) + '_' + person + '.mp3'
    os.rename(src, dst)
    counter += 1

print(f"\nAll {len(mp3_audios)} mp3 audios have been renamed using leading "
      f"zeroes, person's name and said word. Ranging from {start} to {end}.")
