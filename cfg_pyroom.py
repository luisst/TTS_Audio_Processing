import sys
import os
import shutil

def check_folder(this_dir, subf = False):
    '''If {this_dir} exists, ask if okay to overwrite; otherwise, create it'''
    if not os.path.isdir(this_dir):
        os.mkdir(this_dir)

    if subf == False:
        if len(os.listdir(this_dir)) != 0:
            print(f"{this_dir} isn't empty, is it okay if I overwrite it? [y/n]")
            if input().lower() != 'y':
                sys.exit()
            else:
                shutil.rmtree(this_dir)
                os.mkdir(this_dir)


# ### Allan setup (table)
# shoebox_vals = [1.6, 1.4, 1.2]

# mic_dict = {"mic_0": [0.8, 0.7, 0],
#             "mic_1": [0.81, 0.7, 0]}

# src_dict = {"src_0": [0, 0.622, 0.33], # d = 
#             "src_1": [0.381, 0, 0.432], # d = 
#             "src_2": [1, 1.4, 0.33], # d = 
#             "src_3": [0.762, 0, 0.3]} # d =


# ### Allan setup (extended by +4 +4)
# shoebox_vals = [5.6, 5.4, 2.2]

# mic_dict = {"mic_0": [2.8, 2.7, 0],
#             "mic_1": [2.81, 2.7, 0]}

# src_dict = {"src_0": [2, 2.622, 0.33], # d = 
#             "src_1": [2.381, 2, 0.432], # d = 
#             "src_2": [3, 3.4, 0.33], # d = 
#             "src_3": [2.762, 2, 0.3]} # d =

# ### Phuong setup (table)
# shoebox_vals = [1.6, 1.4, 1.2]

# mic_dict = {"mic_0": [0.8, 0.7, 0],
#             "mic_1": [0.81, 0.7, 0]}

# src_dict = {"src_0": [0.05, 0.533, 0.355], # d = 
#             "src_1": [0.025, 0.92, 0.33], # d = 
#             "src_2": [0.685, 0, 0.381], # d = 
#             "src_3": [0.431, 1.295, 0.33]} # d = 
# ### 0.9144, 1.244, 0.25

# ### Phuong setup (extended +4 +4)
# shoebox_vals = [5.6, 5.4, 2.2]

# mic_dict = {"mic_0": [2.8, 2.7, 0],
#             "mic_1": [2.81, 2.7, 0]}

# src_dict = {"src_0": [2.05, 2.533, 0.355], # d = 
#             "src_1": [2.025, 2.92, 0.33], # d = 
#             "src_2": [2.685, 2, 0.381], # d = 
#             "src_3": [2.431, 3.295, 0.33]} # d = 
# ### 2.9144, 3.244, 0.25


### Paper setup  GT(table)
shoebox_vals_gt_tab = [1.7, 1.5, 1.5]

mic_dict_gt_tab = {"mic_0": [0.75, 0.6, 0],
            "mic_1": [0.85, 0.6, 0]}

src_dict_gt_tab = {"src_0": [0.508, 0, 0.355], # d = 
            "src_1": [0, 0.787, 0.432], # d = 
            "src_2": [0, 1.219, 0.469], # d = 
            "src_3": [0.787, 1.371, 0.457]} # d = 

# ### Paper setup GT (extended +4 +4)
shoebox_vals_gt_ext = [5.5, 5.2, 2.2]

mic_dict_gt_ext = {"mic_0": [2.75, 2.6, 0],
            "mic_1": [2.85, 2.6, 0]}

src_dict_gt_ext = {"src_0": [2.508, 2, 0.355], # d = 
            "src_1": [2, 2.787, 0.432], # d = 
            "src_2": [2, 3.219, 0.469], # d = 
            "src_3": [2.787, 3.371, 0.457]} # d = 


### Paper setup  Baseline(table)
shoebox_vals_bs_tab = [1.3, 1.3, 1.5]

mic_dict_bs_tab = {"mic_0": [0.4955, 0.477, 0],
            "mic_1": [0.5955, 0.477, 0]}

src_dict_bs_tab = {"src_0": [0.496, 0.137, 0.368], # d = 
            "src_1": [0, 0.477, 0.368], # d = 
            "src_2": [0.33, 1.056, 0.368], # d = 
            "src_3": [0.661, 1.056, 0.368]} # d = 

# ### Paper setup Baseline (extended +4 +4)
shoebox_vals_bs_ext = [4.991, 4.954, 2.2]

mic_dict_bs_ext = {"mic_0": [2.4955, 2.477, 0],
            "mic_1": [2.5955, 2.477, 0]}

src_dict_bs_ext = {"src_0": [2.496, 2.137, 0.368], # d =
            "src_1": [2, 2.477, 0.368], # d =
            "src_2": [2.33, 3.056, 0.368], # d =
            "src_3": [2.661, 3.056, 0.368]} # d =

# ### Paper setup EST (table)
shoebox_vals_pred_tab = [1.6, 1.5, 1.5]

mic_dict_pred_tab = {"mic_0": [0.5, 0.45, 0],
            "mic_1": [0.6, 0.45, 0]}

src_dict_pred_tab = {"src_0": [0.482, 0.705, 0.357], # d =
            "src_1": [0, 0.705, 0.516], # d =
            "src_2": [0.177, 1.328, 0.510], # d =
            "src_3": [0.898, 1.328, 0.334]} # d =

# ### Paper setup EST (extended +4 +4)
shoebox_vals_pred_ext = [5, 4.95, 2.2]

mic_dict_pred_ext= {"mic_0": [2.5, 2.45, 0],
            "mic_1": [2.6, 2.45, 0]}

src_dict_pred_ext  = {"src_0": [2.482, 2.705, 0.357], # d =
            "src_1": [2, 2.705, 0.516], # d =
            "src_2": [2.177, 3.328, 0.510], # d =
            "src_3": [2.898, 3.328, 0.334]} # d =

all_cfg = {"gt_ext":[shoebox_vals_gt_ext, mic_dict_gt_ext, src_dict_gt_ext] }
           


# all_cfg = {"pred_tab": [shoebox_vals_pred_tab, mic_dict_pred_tab, src_dict_pred_tab],
#            "pred_ext": [shoebox_vals_pred_ext, mic_dict_pred_ext, src_dict_pred_ext],
#            "bs_tab": [shoebox_vals_bs_tab, mic_dict_bs_tab, src_dict_bs_tab],
#            "bs_ext": [shoebox_vals_bs_ext, mic_dict_bs_ext, src_dict_bs_ext],
#            "gt_tab":[shoebox_vals_gt_tab, mic_dict_gt_tab, src_dict_gt_tab],
#            "gt_ext":[shoebox_vals_gt_ext, mic_dict_gt_ext, src_dict_gt_ext]}


### Original setup
# shoebox_vals = [6, 7, 2.2]

# mic_dict = {"mic_0": [3, 4, 0],
#             "mic_1": [3.1, 4, 0]}

# src_dict = {"src_0": [4, 5.75, 1], # d = 2.345 | 2D: 1.8
#             "src_1": [2, 6.5, 1.5], # d = 4.123 | 2D: 3.6
#             "src_2": [1, 3.5, 1.5], # d = 5.2201 | 2D: 5
#             "src_3": [4.5, 2, 1]} # d = 6.8738 | 2D: 6.7


i_list = [0,1,2,3]

abs_coeff = 0.7

fs = 16000
