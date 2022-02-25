import os
import sys
import pandas as pd
from num2words import num2words
import re
import shutil
import soundfile as sf
import subprocess as subp
import glob

from phonemizer import phonemize
from phonemizer.separator import Separator

sys.path.append("./../../04_Audio_Perfomance_Evaluation")
from my_files_utils import *

sr = 16000

### --------------------------------- 03_TTS_to_NPY -------------------------------------
def find_error_lines(transcript_path, words_with_errors):

    old_transcr = open(transcript_path, 'r')


    lines_to_change = []
    for idx, line in enumerate(old_transcr):
        for word in words_with_errors.keys():
            if bool(re.search(word, line)):
                line = line.replace(word, words_with_errors[word])
                str_2_log = f'{idx} - {word}: {line}'
                # print(str_2_log)
                lines_to_change.append((idx, line))

    return lines_to_change

def check_binary(string) :

    # set function convert string
    # into set of characters .
    p = set(string)

    # declare set of '0', '1' .
    s = {'0', '1'}

    # check set p is same as set s
    # or set p contains only '0'
    # or set p contains only '1'
    # or not, if any one condition
    # is true then string is accepted
    # otherwise not .
    if s == p or p == {'0'} or p == {'1'}:
        return True
    else :
        return False

def convert_numbers_text(input_text):

    # to lower case
    std_text_input = input_text.lower()

    # analize each word if binary or not
    std_list_output = []
    for current_word in std_text_input.split(' '):

        binary_words = []
        if check_binary(current_word):
            for current_digit in list(current_word):
                binary_words.append(num2words(current_digit))
            processed_word = ' '.join(binary_words)
            # print(f'Binary found! {processed_word}')
        elif current_word.isdigit():
            processed_word = num2words(current_word)
            # print(f'{current_word} -> {processed_word}')
        else:
            processed_word = current_word
        std_list_output.append(processed_word)

    joined_output_words = ' '.join(std_list_output)

    # remove extra blanc spaces
    final_word = " ".join(joined_output_words.split())
    return final_word

def detect_lang_transcr(transcript_path):
    tmp_lang = transcript_path.split('_')[-1][:-4]
    if tmp_lang == 'english' or 'spanish':
        return tmp_lang
    else:
        print("Error in the transcript name")
        sys.exit()


def select_people(current_lang):
    if current_lang == 'english':
        return sorted(['Ivy', 'Salli', 'Joey', 'Justin'])
    elif current_lang == 'spanish':
        return sorted(['Mia', 'Penelope', 'Lupe', 'Miguel'])
    else:
        print("Error in the transcript name")
        sys.exit()


### --------------------------------- 03_Login_download_Gecko -------------------------------
def delete_contents(this_dir):
    """Delete contents from folder located in {this_dir}"""
    for item in os.listdir(this_dir):
        if os.path.isfile(this_dir + '/' + item):
            os.remove(this_dir + '/' + item)
        elif os.path.isdir(this_dir + '/' + item):
            shutil.rmtree(this_dir + '/' + item)
        else:
            print(f"I couln't remove this file {this_dir + '/' + item}")
            print("Please try manually. Then, re-run this code.\n")
            sys.exit()


def obtain_phrases_v2(input_folder):
    transcript_path = locate_single_txt(input_folder)
    current_lang = detect_lang_transcr(transcript_path)

    print(transcript_path)
    df = pd.read_csv(transcript_path, usecols= ['Text'])
    phrases_list = df['Text'].values.tolist()

    return phrases_list


### --------------------------------- 04_TTS_to_NPY -------------------------------------
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


def my_phonemizer(input_text, current_language):
    #Parameters for phonemizer
    if current_language == 'english':
        L = 'en-us'
    elif current_language == 'spanish':
        L = 'es-419'
    else:
        print("Error: not defined language for phonemizer")
        sys.exit()
        #language 'es-la' latin-america, 'es' spain
    B_E = 'espeak' #back end
    c_sep = Separator(phone='_', syllable='', word=' ') #custom separator

    phones = phonemize(input_text, L, B_E, c_sep)[:-2]

    return phones


def create_lists_per_person(mp3_base_path, people, input_folder):
    audios_dict = {}

    all_texts = get_list_of_GT(input_folder, single_col=True)
    single_person_len = len(all_texts)
    total_len = single_person_len*len(people)

    for person in sorted(people):
        current_mp3_folder = mp3_base_path+ '/tts_' + person
        person_mp3s = glob.glob("{}/*.mp3".format(current_mp3_folder))

        if single_person_len != len(person_mp3s):
            print(f"ERROR: Number of lines in proto-transcript {single_person_len} different than mp3 folder {person} {len(person_mp3s)}")
            sys.exit()

        audios_dict[person] = sorted(person_mp3s)
    
    print(f'Total length: {total_len}')

    return audios_dict, total_len


def convert_mp3_to_wav(folder_mp3s, folder_wavs, transcript_path, i_start, i_end, people, audios_dict):

    f = open(transcript_path, 'r')
    lines = f.readlines()
    f.close()

    for idx in range(i_start, i_end, 4):
        for idx_person, person in enumerate(sorted(people)):
            pt_audioname = lines[idx + idx_person].split('\t')[0]

            current_mp3_folder = folder_mp3s + '/tts_' + person
            mp3Folder_audioname = audios_dict[person][idx//4].split('/')[-1]

            if mp3Folder_audioname[:-4] != pt_audioname[:-4]:
                print(f'Error in the audio name matching. idx {idx}')
                sys.exit()

            current_wav_path = folder_wavs + '/' + pt_audioname
            current_mp3_path = current_mp3_folder + '/' + mp3Folder_audioname

            cmd = f"ffmpeg -i '{current_mp3_path}' -loglevel quiet -acodec pcm_s16le -ac 1 -ar {sr} {current_wav_path}"
            print(f'audio name {pt_audioname}')

            subp.run(cmd, shell=True)


def create_transcript(mp3_base_path, folder_wavs, 
                      transcript_path, new_transcript_path, 
                      i_start, i_end, 
                      people, audios_dict, 
                      flag_phonemes):
    phonemes_list = []
    wavs_list = []

    f = open(transcript_path, 'r')
    lines = f.readlines()
    f.close()

    for idx in range(i_start, i_end, 4):

        pt_GT = lines[idx].split('\t')[1].strip()
        print(f'{idx}---------------------------------\n')
        if flag_phonemes:
            current_phonemes = my_phonemizer(pt_GT, current_lang)
        else:
            current_phonemes = pt_GT

        for idx_person, person in enumerate(sorted(people)):
            pt_audioname = lines[idx + idx_person].split('\t')[0]
            pt_gt2 = lines[idx + idx_person].split('\t')[1]
            current_mp3_folder = mp3_base_path + '/tts_' + person
            mp3Folder_audioname = audios_dict[person][idx//4].split('/')[-1]

            current_wav_path = folder_wavs + '/' + pt_audioname
            wavs_list.append(current_wav_path)
            phonemes_list.append(current_phonemes)

            print(f'audio name {pt_audioname} - GT: {current_phonemes} - gt: {pt_gt2}')

    columns = ['path', 'GT']
    write_my_csv(wavs_list, phonemes_list, path=new_transcript_path, cols=columns, txt_flag=True, time_format=False)


def check_my_wavs(folder_wavs):
    wav_paths_list = glob.glob("{}/*.wav".format(folder_wavs))

    for current_path in wav_paths_list:
        current_audio, samplerate = sf.read(current_path)

        #Ensure sample rate of audio is the desired sample rate
        if samplerate != sr:
            print(f"ERROR: This file {wav_path} doesn't have a {sr} sample rate")
            sys.exit()

        #Ensure audio is one channel
        if len(current_audio.shape) != 1:
            print(f"ERROR: This file {wav_path} doesn't have 1 channel")
            sys.exit()


def store_to_npy(folder_wavs, npy_path):
    wav_paths_list = glob.glob("{}/*.wav".format(folder_wavs))

    X = []

    print("\nSaving audios in matrix...")

    for idx, current_path in enumerate(wav_paths_list):
        data, _ = sf.read(current_path)
        X.append(np.trim_zeros(data))
        if idx%1000 == 0:
            print(f"\t[{idx+1} / {len(wav_paths_list)}] audios have been added to matrix")

    #Save matrix in .npy file
    np.save(npy_path, X)
    print(f"\nNumpy array has been created and saved here {npy_path}. It is "
        f"composed of {len(wav_paths_list)} rows")

