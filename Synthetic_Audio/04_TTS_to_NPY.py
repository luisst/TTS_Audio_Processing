import os
import subprocess as subp
import sys

from phonemizer import phonemize
from phonemizer.separator import Separator

from utils import delete_contents
import pandas as pd


def obtain_phrases(input_folder, current_lang):
    for file in sorted(os.listdir(input_folder)):
        if file.endswith('_{}.csv'.format(current_lang)):
            file_path = input_folder + '/' + file
            print(file_path)
            df = pd.read_csv(file_path, usecols= ['Text'])
            phrases_list = df['Text'].values.tolist()


    return phrases_list

def check_folder(this_folder):
    #Make sure {this_folder} exists. If it does, ask if ok to continue
    if not os.path.isdir(this_folder):
        os.mkdir(this_folder)

    if len(os.listdir(this_folder)) != 0:
        print(f"\n{this_folder} isn't empty, please pick one of these options:"
              "\n - 'c' for continue\n - 'q' for quit\n - 'd' for delete")
        answer = input()
        if answer == 'd':
            delete_contents(this_folder)
            print(f"\nContents in {this_folder} have been deleted.")
        elif answer != 'c':
            print("Okay, terminating the program now")
            sys.exit()

'''Convert audios from MP3 to WAV. Change sample rate from 22,050Hz to 16,000.
Apply this, only to audios which words have 3 or more characters. Create
transcript that has two columns: full wav path and phoneme sequence of word
said in audio.

Check the tts_making_corrections.py file. There are a few audios that didn't
download correctly (and some typos), so I am removing them from the
{folder_wavs} folder.'''

# Desired sample rate for wav files
sr = 16000
person = 'Penelope' #Options are: ['Mia', 'Miguel', 'Lupe', 'Penelope']

folder_mp3s = '/home/luis/Documents/ExtendedGT/tts_orig/' + person
folder_wavs = '/home/luis/Documents/ExtendedGT/tts_wavs'
folder_person = folder_wavs + '/' + person
transcript = folder_person + '/transcript.txt'

# Make sure folders exist. If they do, ask if ok to  continue
check_folder(folder_wavs)
check_folder(folder_person)

input_folder = './OutputCSV'
lang_list = ['english', 'spanish']
lang_idx = 1

#Parameters for phonemizer
if lang_list[lang_idx] == 'english':
    L = 'en-us'
elif lang_list[lang_idx] == 'spanish':
    L = 'es-la'
else:
    print(" error ")
    #language 'es-la' latin-america, 'es' spain
B_E = 'espeak' #back end
c_sep = Separator(phone='_', syllable='', word=' ') #custom separator

counter = 0
F = open(transcript, 'w')


vocabulary = obtain_phrases(input_folder, lang_list[lang_idx])

for idx, audio in enumerate(sorted(os.listdir(folder_mp3s))):
    word = vocabulary[idx]
    phones = phonemize(word, L, B_E, c_sep)[:-2]
    # print(audio)
    mp3_path = folder_mp3s + '/' + audio
    wav_path = folder_person + '/' + audio[:-4] + '.wav'
    F.write(wav_path + '\t' + phones + '\n')
    cmd = f"ffmpeg -i '{mp3_path}' -acodec pcm_s16le -ac 1 -ar {sr} {wav_path}"
    subp.run(cmd, shell=True)
    counter += 1

F.close()

print(f"From all {idx+1} audios in {folder_mp3s}, {counter} were converted "
      f"to wav format and saved here {folder_wavs}")


'''/**************************************************************************

    Read lines from custom transcript. Grab wav_path from each line, read the
    file (get the wave) from such and save it in a row of a numpy array. In
    other words, we prepare the audios listed in the transcript to be inputted
    in our Pyroomacoustics code. We zero pad all audios with repsect to the
    longest audio in the transcript.

***************************************************************************'''
import numpy as np
import os
import soundfile as sf
import sys

transcript = '/home/luis/Documents/ExtendedGT/tts_wavs/Penelope/transcript.txt'
save_file = '/home/luis/Documents/ExtendedGT/TS1_penelope_spanish.npy'
SR = 16000 #Desired sample rate for all audios

#Check if {save_file} already exists. Ask if okay to continue.
if os.path.exists(save_file):
    print(f"This file {save_file} already exists. If we continue, it will be "
          "overwritten...do you want to continue? [y/n] ")
    if input() != 'y':
        sys.exit()

f = open(transcript, 'r')
lines = f.readlines()
# lines = lines[:5000]
f.close()

#Determine number of audios in transcript as well as the shape of longest audio
print("Determining longest audio...")
audios_lengths = []
for idx, line in enumerate(lines):
    wav_name = line.split('\t')[0]
    data, samplerate = sf.read(wav_name)

    #Ensure sample rate of audio is the desired sample rate
    if samplerate != SR:
        print(f"ERROR: This file {wav_name} doesn't have a {SR} sample rate")
        sys.exit()

    #Ensure audio is one channel
    if len(data.shape) != 1:
        print(f"ERROR: This file {wav_name} doesn't have 1 channel")
        sys.exit()

    audios_lengths.append(data.shape[0])

    if idx%500 == 0:
        print(f"\t[{idx+1} / {len(lines)}] audios have been scanned")

#Initialize matrix that will hold wave samples of all audios (zero padded)
max_len = max(audios_lengths)
X = np.zeros((len(lines), max_len))

print("\nSaving audios in matrix...")
for idx, line in enumerate(lines):
    wav_name = line.split('\t')[0]
    data, _ = sf.read(wav_name)
    X[idx][0:data.shape[0]] = data
    if idx%1000 == 0:
        print(f"\t[{idx+1} / {len(lines)}] audios have been added to matrix")

#Save matrix in .npy file
np.save(save_file, X)
print(f"\nNumpy array has been created and saved here {save_file}. It is "
      f"composed of {len(lines)} rows and {max_len} columns.")
