#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 14:40:43 2021

@author: luis
"""
import glob
import os
import sys
import torch
import shutil
import re
import numpy as np
from os.path import join as pj
from os.path import exists

from torchaudio.transforms import MelSpectrogram as MelSpec

import pickle

from phonemizer import phonemize
from phonemizer.separator import Separator

#Sample Rate
SR = 16000 
mels = 128

def check_empty_folders_list(src_dir, src_folders):
    
    numpys_src_folders = []
    
    for idx, folder in enumerate(src_folders):
        
        current_folder_path = pj(src_dir, folder)   
        if check_empty_folder(current_folder_path):
            check_ending_format(current_folder_path, '_ALL')
            numpys_src_folders.append(current_folder_path)
    
    return numpys_src_folders


def check_necessary_data(required_data_path):
    
    req_met_flag = exists(required_data_path)
    
    return req_met_flag


def check_folder_for_process(this_dir):
    '''If {this_dir} exists, ask if okay to overwrite.
        Return True to start process'''
    compute_procedure = False
    
    if not os.path.isdir(this_dir):
            os.mkdir(this_dir)
            compute_procedure = True
            
    if len(os.listdir(this_dir)) != 0:
        print(f"{this_dir} isn't empty, is it okay if I overwrite it? [y/n]")
        if input().lower() != 'y':
            print('Content was not modified') 
        else:
            shutil.rmtree(this_dir)
            os.mkdir(this_dir)
            compute_procedure = True
    else:
        print('Folder: {} is empty. Proceed with computation.'.format(this_dir))
        compute_procedure = True
    
    return compute_procedure


def check_empty_folder(current_folder_path):
    """ Return true if folder is NOT empty """
    
    if (len(os.listdir(current_folder_path)) != 0):    
       return True
    else:
        print("Folder is empty")
        return False
    
def check_ending_format(current_folder_path, ending_format_substring):
    if current_folder_path[-4:] != ending_format_substring:
        print("Error in the format, must end with {}!".format(ending_format_substring))
        sys.exit()

def locate_single_txt(src_dir):
    all_texts = glob.glob("{}/*.txt".format(src_dir))

    if len(all_texts) != 1:
        print("Too many transcripts! Please use only 1")
    else:
        input_transcript_path = all_texts[0]
        print(input_transcript_path)
        print("\n")

    return input_transcript_path


def check_for_subcode(current_folder_path, sub):
    """ Return true if folder is NOT empty """
    
    list_npys_present = glob.glob("{}/*.npy".format(current_folder_path))

    my_res = [s for s in list_npys_present if sub.lower() in s.lower()]
    
    if (len(my_res) > 1):
        print("Multiple files found with same subcode {}".format(sub))
        return False
    elif (len(my_res) == 1):
        return True
    elif (len(my_res) == 0):
        return False
    else:
        return False 

def normalize_0_to_1(matrix):
    """Normalize matrix to a 0-to-1 range; code from
    'how-to-efficiently-normalize-a-batch-of-tensor-to-0-1' """
    d1, d2, d3 = matrix.size() #original dimensions
    matrix = matrix.reshape(d1, -1)
    matrix -= matrix.min(1, keepdim=True)[0]
    matrix /= matrix.max(1, keepdim=True)[0]
    matrix = matrix.reshape(d1, d2, d3)
    return matrix


def TS_npy_to_spctrgrms(tts_gtts, npy_output_path, SR, mels):
    '''Use resulting numpy array from Pyroomacoustics to generate respective
    spectrograms. Use original audios to determine original lengths, since
    rows from numpy array were 0-padded to the longest audio in the dataset'''
    print(f"Started processing {npy_output_path.split('/')[-1]}...")
    sr_coeff = SR / 1000 #divide by 1000 to save audio's duration in milisecs
    
    np_array = np.load(npy_output_path, allow_pickle=True)
    
    #Grab audio waves from {npy_file} and transcript lines from {transcript}
    f = open(tts_gtts['old_transcr'], 'r')
    lines = f.readlines()
    f.close()
    
    #Ensure {lines} and {np_array} have the same number of rows (lines)
    if len(lines) != np_array.shape[0]:
        print("ERROR: transcript and npy_file do not share the same # of rows\n")
        sys.exit()
    
    #Iterate through each line in old transcript
    F = open(tts_gtts['new_transcr'], 'w')
    for idx, line in enumerate(lines):
        #Grab samples from npy file
        audio_samples_np = np_array[idx]
        
        #Samples from npy file are zero padded; these 3 lines will 'unpad'.
        audio_orig_path, text = line.strip().split('\t')
        # orig_samples, _ = torchaudio.load(audio_orig_path)
        audio_dur = int(len(audio_samples_np) / sr_coeff) # audio's duration
        
        #Convert from numpy array of integers to pytorch tensor of floats
        audio_samples_pt = torch.from_numpy(audio_samples_np)
        
        # temp_path = f"/home/luis/Desktop/{idx}.wav"
        # torchaudio.save(temp_path, audio_samples_pt, SR)
        
        audio_samples_pt = torch.unsqueeze(audio_samples_pt, 0)
        #Uncomment line below if npy output is int
        audio_samples_pt = audio_samples_pt.type(torch.FloatTensor)
        
        #Calculate spectrogram and normalize
        spctrgrm = MelSpec(sample_rate=SR, n_mels=mels)(audio_samples_pt)
        spctrgrm = normalize_0_to_1(spctrgrm)
        
        #Get spectrogram path (where it will be saved)
        filename = audio_orig_path.split('/')[-1]
        spctrgrm_path = tts_gtts['dst_dir'] + '/' + filename[:-4] + '.pt'
        
        #Save spectrogram and save information in new transcript
        torch.save(spctrgrm, spctrgrm_path)
        F.write(spctrgrm_path + '\t' + text + '\t' + str(audio_dur) + '\n')
        
        if idx%1000 == 0:
            print(f"\t{idx+1} spectrograms have been processed and saved")
        
                       
    print(f"...finished, all {idx+1} spectrograms have been created. Samples of"
          " original audios and samples of pyroom audios have been plotted.\n")
    
    F.close()
   



def calculate_output_paths(current_folder_path):
    
    new_transcr_path = current_folder_path + '/' + '/transcript.txt'
    
    file = sorted(glob.glob("{}/*.npy".format(current_folder_path)))[0]
    
    if file[-7:] != '_x4.npy':
        full_string = file.split('/')[-1]
        trg_substring = '_DA_'
        list_of_strings = [m.start() for m in re.finditer(trg_substring, full_string)]
        
        if len(list_of_strings) != 1:
            print("Name is weird!")
    
        sub_start_idx = list_of_strings[0]        
        npy_output_name = full_string[:sub_start_idx] + \
                full_string[sub_start_idx+len(trg_substring)+1:-4] + \
                '_x4.npy'
        
        npy_output_path = current_folder_path + '/' + npy_output_name
        
        dataset_name = full_string[:sub_start_idx] + \
                full_string[sub_start_idx+len(trg_substring)+1:-4]

    return new_transcr_path, npy_output_path, dataset_name
   
def merge_x4_pyroom(current_folder_path, 
                    new_transcr_path, npy_output_path,
                    src_transcr_path):
    
    src_transcr = open(src_transcr_path, 'r')
    lines = src_transcr.readlines()
    src_transcr.close()
        
    new_transcr = open(new_transcr_path, 'w')
    
    All_npys = []
            
    for file in sorted(glob.glob("{}/*.npy".format(current_folder_path))):
        full_string = file.split('/')[-1]
        trg_substring = '_DA_'
        list_of_strings = [m.start() for m in re.finditer(trg_substring, full_string)]
        sub_start_idx = list_of_strings[0]
        DA_number = full_string[sub_start_idx+len(trg_substring):sub_start_idx+len(trg_substring)+1]
                
        current_DA = np.load(file, allow_pickle=True)
        print("Loaded DA {}".format(DA_number))
        
        All_npys = np.concatenate((All_npys, current_DA), axis=0)
        print("NPY DA Concatenated")
        
        for line in lines:
            old_path, text = line.split('\t')
            old_name = old_path.split('/')[-1].split('.')[0]
            new_path = old_name + trg_substring + str(DA_number) + '.wav'
    
            new_transcr.write(f"{new_path}\t{text}")
    
    
    new_transcr.close()
    
    np.save(npy_output_path, All_npys)
    print("Saving np load {}".format(npy_output_path))
   
    return
   
def create_dicts(transcr_path, dicts_path, dataset_name):
    L = 'es-419'
    B_E = 'espeak' #back end
    c_sep = Separator(phone='_', syllable='', word=' ') #custom separator
    
    dict_txt = dicts_path + '/{}_dict.txt'.format(dataset_name)
    dict_pickle = dicts_path + '/{}_dict.pickle'.format(dataset_name)
    
    #Get vocabulary, list of unique words in TTS-gTTS's transcript
    print("Processing TTS-gTTS's Transcript...")
    vocabulary = []
    transcr = open(transcr_path, 'r')
    for idx, line in enumerate(transcr):
        _, text, _ = line.split('\t')
        words = text.split(' ')
        for word in words:
            if word not in vocabulary:
                #no need to apply .lower to {word}; already done in previous code
                vocabulary.append(word)
                
        if idx%100 == 0:
            print(f"\t{idx+1} lines scanned")
                  
    print(f" ...Finished, all {idx+1} lines have been scanned\n")
    transcr.close()
    
    #Sort vocabulary
    vocabulary = sorted(vocabulary)
    print(f"I found {len(vocabulary)} unique words in the transcript\n")
    
    #Start 'phonemization'
    print("'Phonemization' of words has started...")
    Dictionary = {}
    Dict = open(dict_txt, 'w')
    for idx, word in enumerate(vocabulary):
        phones = phonemize(word, L, B_E, c_sep)[:-2]
        phones = phones.replace('_', ' ')
        
        #Give warning if word has an 'empty' phoneme
        for ph in phones.split(' '):
            if ph == '':
                print(f"\tWARNING: This word '{word}' has an empty phoneme")
        
        Dict.write(word + '\t' + phones + '\n')
        Dictionary[word] = phones
    
        if idx % 500 == 0:
            print(f"\t[{idx+1}/{len(vocabulary)}] words have been phonemized...")
        
    Dict.close()
    print(f" ...Finished. All {idx+1} words have been phomemized.\n")
    
    #Save {Dictionary} in pickle file
    pickle.dump(Dictionary, open(dict_pickle, "wb"))
    print(f".txt dictionary has been saved here {dict_txt}")
    print(f".pickle dictionary has been saved here {dict_pickle}")
    

