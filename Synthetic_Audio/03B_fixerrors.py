
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

person = 'Joey' #['Ivy', 'Salli', 'Joey', 'Justin']
avoid_words = {'Mia': [], 'Miguel': [], 'Penelope': [], 'Lupe': [],
               'Joey': [], 'Ivy': [], 'Justin': []}

index_of_error = 1760
index_of_error -= 1 # Add one because the index came from Sublime, and them starts with a 1

start = 0
end = index_of_error

input_folder = dir_path + '/input_txts'
lang_list = ['english', 'spanish']

# find language idx based on the name of the file
# create a new utils functions to deal with file extraction
lang_idx = 0

vocabulary = obtain_phrases(input_folder, lang_list[lang_idx])

print(vocabulary[index_of_error])
folder_mp3 = dir_path + '/tts_' + person

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
for word, audio in zip(vocabulary[start:end + 1], mp3_audios):
    src = folder_mp3 + '/' + audio
    index = str(start + counter)
    dst = folder_mp3 + '/' + index.zfill(4) + '_' + person + '.mp3'
    os.rename(src, dst)
    counter += 1

print(f"\nAll {len(mp3_audios)} mp3 audios have been renamed using leading "
      f"zeroes, person's name and said word. Ranging from {start} to {end}.")
