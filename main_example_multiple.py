import numpy as np
import sounddevice as sd
import os.path
import pickle
import time

from cfg_pyroom import fs, check_folder, all_cfg
from DA_pyroom import DAwithPyroom


"""
the conda environmet is ctc_audio
"""

USER_HOME_PATH = os.path.expanduser('~')
INPUT_NPY_PATH = r'/home/luis/Dropbox/dataset_TTS_fromTxtTestset/05_Pyroom_NPY/Npy_input/TS1_lupe_spanish.npy'

NOISE_PATH_Audioset = USER_HOME_PATH + r'/Dropbox/DATASETS_AUDIO/Noisy-Speech_Acoustics_Sim_NOISES/Noises_all.npy'
NOISE_PATH = USER_HOME_PATH + r'/Dropbox/DATASETS_AUDIO/Noisy-Speech_Acoustics_Sim_NOISES/AOLME_noises.npy'

BASE_PATH = '/'.join(INPUT_NPY_PATH.split('/')[:-1])
NPY_NAME = INPUT_NPY_PATH.split('/')[-1]
output_folder = BASE_PATH + r'/' + r'DataAugmented'

check_folder(output_folder)
output_dir = output_folder + r'/'

t_start = time.time()
t_perf_start = time.perf_counter()
t_pc_start = time.process_time()

data_augmentation_flag = True
float_flag = True

top_select = [1,4]

if (data_augmentation_flag):
    outer_ite = 4*len(all_cfg)
else:
    outer_ite = len(all_cfg)


glb_ite = 0

for cfg_key in all_cfg:
    current_cfg = all_cfg[cfg_key]
    cfg_name = str(cfg_key)
    print(cfg_name)

    for position_idx in range(0, top_select[data_augmentation_flag]):
        OUTPUT_PATH = output_dir + NPY_NAME[:-4] + '_DA_{}_{}'.format(position_idx, cfg_name)
        print('Name {}, position {}'.format(NPY_NAME, position_idx))

        # Init class DA with pyroom
        my_sim = DAwithPyroom(INPUT_NPY_PATH, NOISE_PATH, current_cfg, DA_number = position_idx,
                              float_flag=float_flag,
                              ds_name=NPY_NAME, total_ite=outer_ite, num_ite = glb_ite)

        # Call method sim_dataset to create simulated dataset
        my_dataset_simulated, glb_ite = my_sim.sim_dataset(position=position_idx)

        # Save GT
        np.save(OUTPUT_PATH, my_dataset_simulated)

# Listen to a sample from the simulation
# sd.play(my_dataset_simulated[1,:], fs)

t_end = time.time()
t_perf_end = time.perf_counter()
t_pc_end = time.process_time()

print("Total time time : {}".format(t_end - t_start))
print("Total time perf_counter: {}".format(t_perf_end - t_perf_start))
print("Total time process_time : {}".format(t_pc_end - t_pc_start))




