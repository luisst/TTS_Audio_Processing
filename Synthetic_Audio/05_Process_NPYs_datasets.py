'''/**************************************************************************

Given four different outputs of Pyroom, merge them all into one folder.

Setup: place x4 npys in each folder. Parent folder should contain the transcript as txt

***************************************************************************'''
import os
import time
from os.path import join as pj

from numpys_to_dataset_utils import locate_single_txt, check_empty_folder, \
                                    check_for_subcode, TS_npy_to_spctrgrms, \
                                    check_folder_for_process, create_dicts, merge_x4_pyroom, \
                                    check_ending_format, SR, mels, calculate_output_paths, \
                                    check_empty_folders_list, check_necessary_data




src_dir = '/home/luis/Documents/TS_SP_phrases'

calculate_specs = True
calculate_dicts = True

input_transcript_path = locate_single_txt(src_dir)
src_transcr_path = pj(src_dir, 'transcript.txt')


src_folders = sorted([name for name in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, name))])

# filter folders that are empty
numpys_src_folders = check_empty_folders_list(src_dir, src_folders)

t_start = time.time()
t_perf_start = time.perf_counter()
t_pc_start = time.process_time()

for idx, folder in enumerate(numpys_src_folders):
    current_folder_path = pj(src_dir, folder)

    new_transcr_path, \
    npy_output_path, \
    dataset_name = calculate_output_paths(current_folder_path)

    spec_folder_name = current_folder_path.split('/')[-1][:-4]
    spec_folder_name = spec_folder_name + '_spec'
    spec_dest_path = pj(current_folder_path, spec_folder_name)

    if not(check_for_subcode(current_folder_path, '_x4')):
        merge_x4_pyroom(current_folder_path, new_transcr_path,
                        npy_output_path, src_transcr_path)


    if calculate_specs:
        # Create the name of the destination folder
        compute_specs = check_folder_for_process(spec_dest_path)

        # Create spectrograms
        TS = {'old_transcr': '{}'.format(new_transcr_path),
            'new_transcr': '{}/transcript.txt'.format(spec_dest_path),
            'dst_dir': '{}'.format(spec_dest_path)}

        if compute_specs:
            TS_npy_to_spctrgrms(TS, npy_output_path, SR, mels)


    if calculate_dicts:
        # Create dicts
        dicts_path = current_folder_path + '/dicts'        
        specs_transcript_path = spec_dest_path+'/transcript.txt'

        compute_dicts = check_folder_for_process(dicts_path)
        req_met_flag = check_necessary_data(specs_transcript_path)

        
        
        if compute_dicts and req_met_flag:
            print("Creating the dicts for: {}".format(dataset_name))
            create_dicts(specs_transcript_path, dicts_path, dataset_name)

# what happen when some have specs??
t_end = time.time()
t_perf_end = time.perf_counter()
t_pc_end = time.process_time()

print("Total time time : {}".format(t_end - t_start))
print("Total time perf_counter: {}".format(t_perf_end - t_perf_start))
print("Total time process_time : {}".format(t_pc_end - t_pc_start))

# add wait time 90 seconds , otherwise, skip and print at the end which files were skipped.
