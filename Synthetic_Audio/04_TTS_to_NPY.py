
import sys


from utils_functions_tts_process import check_folder, detect_lang_transcr, \
                                        select_people, my_phonemizer, \
                                        create_lists_per_person, convert_mp3_to_wav, \
                                        create_transcript, store_to_npy, \
                                        check_my_wavs



flag_phonemes = False
flag_transcript = True
flag_wavs = False
flag_NPY = False

name_of_npy = 'eng_feb05_slim'
name_of_transcript = 'transcript'

DATASET_AUDIO_PATH = '/home/luis/Dropbox/DATASETS_AUDIO/TTS_ENG_FEB05'

transcript_path ='/home/luis/Dropbox/DATASETS_AUDIO/TTS_ENG_FEB05/Input_transcripts/proto-transcript_tts_feb05_5K_english.txt'



####### ---------------------------------------------------------------- #######
current_lang = detect_lang_transcr(transcript_path)
people = select_people(current_lang)

folder_mp3s = DATASET_AUDIO_PATH + '/' + 'MP3_original'
folder_input_transcript = DATASET_AUDIO_PATH + '/' + 'Input_transcripts/input_txts'
folder_wavs = DATASET_AUDIO_PATH + '/WAVS'
folder_NPY = DATASET_AUDIO_PATH + '/NPYs'

npy_path = DATASET_AUDIO_PATH + '/' + 'NPYs/' + name_of_npy + '.npy'
new_transcript_path = folder_wavs + '/' + name_of_transcript + '.csv'


audios_dict, total_len = create_lists_per_person(folder_mp3s, people, folder_input_transcript)

if flag_wavs:
    check_folder(folder_wavs) # if i_start > zero dont check
    i_start = 0
    i_end = total_len

    convert_mp3_to_wav(folder_mp3s, folder_wavs, transcript_path, i_start, i_end, people, audios_dict)

    check_my_wavs(folder_wavs)

if flag_transcript:
    i_start = 0 # move this index to the top
    i_end = total_len
    create_transcript(folder_mp3s, folder_wavs, transcript_path, new_transcript_path, i_start, i_end, people, audios_dict, flag_phonemes)

if flag_NPY:
    check_folder(folder_NPY) # add this function into the general one,
    store_to_npy(folder_wavs, npy_path)


