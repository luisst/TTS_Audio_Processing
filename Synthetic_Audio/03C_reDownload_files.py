
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
import subprocess as subp
import os
import glob
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

from utils_functions_tts_process import find_error_lines, detect_lang_transcr, select_people, check_folder

sys.path.append("./../../04_Audio_Perfomance_Evaluation")
from my_files_utils import *

# def obtain_missing_words(txt_missing.txt):


use_login = False

words_with_errors = {'aolme': 'a ol me', 'alome':'a ol me'}

dir_path = os.path.dirname(os.path.realpath(__file__))

input_folder = dir_path + '/input_txts'


transcript_path = locate_single_txt(input_folder)
current_lang = detect_lang_transcr(transcript_path)
people = select_people(current_lang)

lines_to_change = find_error_lines(transcript_path, words_with_errors)
sr = 16000

# person = 'Salli' #['Ivy', 'Salli', 'Joey', 'Justin']
people = ['Ivy', 'Justin', 'Joey']

lines_to_change = [(1000, 'did i go too far?'), 
                   (2000, 'i will do something better'), 
                   (3000, 'oh remembering all those facts?'), 
                   (4000,'i want to watch the video game, again')]
new_folder_name = 'therest'

start_time = time.time()

for person in people:
    if use_login:
        tts_link = 'https://ttsmp3.com/login.php'
        #Load credentials (saved as environmental variables)
        usr = os.environ['TTS_USR']
        psw = os.environ['TTS_PSW']
        Login_Xpath = '/html/body/div[2]/form/input[3]'
    else:
        tts_link = 'https://ttsmp3.com'


    #Folder where audios will be saved
    folder_mp3 = dir_path + '/tts_{}_'.format(new_folder_name) + person

    check_folder(folder_mp3)


    #Setup Firefox's settings so that it doesn't ask for download confirmation
    fp = FirefoxProfile("/home/luis/.mozilla/firefox/i8o6kjlt.selena")
    fp.set_preference("browser.download.folderList",2)
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    fp.set_preference("browser.download.dir", folder_mp3)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/mp3")

    #Grab driver, open website and assert
    driver = webdriver.Firefox(firefox_profile=fp)
    driver.get(tts_link)
    assert "ttsMP3" in driver.title

    if use_login:
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

    word_idx = 1
    total_words_num = len(lines_to_change)
    for idx, gt_txt in lines_to_change:
        my_perct = (word_idx*100)/total_words_num
        print(f'{my_perct:.2f} - {gt_txt}')
        word_idx += 1
        select = Select(driver.find_element_by_id("sprachwahl"))
        select.select_by_value(person)
        time.sleep( 2 ) #Give it time to select value
        text_area = driver.find_element_by_id("voicetext")
        text_area.send_keys(gt_txt)

        download_button = driver.find_element_by_id("downloadenbutton")
        download_button.click()
        time.sleep(2.5) #Give it time to download
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


    all_texts = get_list_of_GT(input_folder, single_col=True)

    fixed_mp3s = sorted(glob.glob("{}/*.mp3".format(folder_mp3)))

    folder_idx = 0
    for idx, gt_txt in lines_to_change:
        src = fixed_mp3s[folder_idx]
        folder_idx += 1
        dst_mp3 = folder_mp3 + '/' + str(idx).zfill(4) + '_' + person + '.mp3'
        wav_path = folder_mp3 + '/' + str(idx).zfill(4) + '_' + person + '.wav'
        print(f'before: {src} | \n after: {dst_mp3} | \n txt: {all_texts[idx]}\n--------------------------')
        os.rename(src, dst_mp3)
        cmd = f"ffmpeg -i '{dst_mp3}' -acodec pcm_s16le -ac 1 -ar {sr} {wav_path}"
        subp.run(cmd, shell=True)

    # eliminate mp3 files

end_time = time.time()
print(f'Total time {(end_time - start_time):.2f}')
if (end_time - start_time) > 400:
    time_in_hours = (end_time - start_time)/60/60
    print(f'Total time hours {time_in_hours:.2f}')
