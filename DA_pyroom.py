#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 10:48:43 2021

@author: luis
"""

import random
import numpy as np
import pyroomacoustics as pra
import time
import librosa
import inspect
import pdb

from cfg_pyroom import abs_coeff, fs, i_list


class DAwithPyroom(object):
    """
    Class for audio simulation using pyroom.
    input signal + 4 random crosstalk + background noise
    """

    def __init__(self, input_path, noise_path,
                 room_cfg, DA_number, float_flag=True, ds_name='0',
                 total_ite=1, num_ite = 0):
        """
        Start the class with the dataset path and turn the float32 flag for
        output format, False for int16 format
        """
        self.x_data = np.load(input_path)
        self.noise_data = np.load(noise_path, allow_pickle=True)
        self.float_flag = float_flag
        self.ds_name = ds_name
        self.room_cfg = room_cfg

        # Numpy output array according to the desired output
        self.x_data_DA = []
        self.num_ite = num_ite
        self.DA_number = DA_number
        self.num_total = int((self.x_data).shape[0]*total_ite)

        global counter_small
        counter_small = 0


    def gen_random_on_range(self, lower_value, max_value):
        """
        generates a random value between lower_value and max_value.
        """
        return round(lower_value + random.random()*(max_value - lower_value),
                     2)


    def eliminate_noise_ending(self, signal):
        """
        Count using a non-optimized python alg the number of zeros
        at the end of the numpy array
        """

        # real_length is initialized with the total length of the signal
        real_length = int(len(signal))
        while abs(signal[real_length - 1]) < 0.0001:
            real_length = real_length - 1

        signal_trimmed = signal[0:real_length]
        return signal_trimmed

    def eliminate_noise_start_ending(self, signal, th):
        """
        Count using a non-optimized python alg the number of zeros
        at the end of the numpy array
        """

        # real_length is initialized with the total length of the signal
        real_length_end = int(len(signal))
        while abs(signal[real_length_end - 1]) < th:
            real_length_end = real_length_end - 1

        signal_trimmed_end = signal[0:real_length_end]
        
        real_length_start = 0
        while abs(signal_trimmed_end[real_length_start]) < th:
            real_length_start = real_length_start + 1
        
        
        signal_trimmed = signal_trimmed_end[real_length_start:]
        
        return signal_trimmed


    def n32(self, audio_float32, gain_value=1):
        """
        Normalize float32 audio with the gain value provided
        """
        if audio_float32.dtype.kind != 'f':
            raise TypeError("'dtype' must be a floating point type")

        vmin = audio_float32.min()
        vmax = audio_float32.max()

        audio_gained = audio_float32*gain_value

        vmin_gained = audio_gained.min()
        vmax_gained = audio_gained.max()

        # try_inspect = inspect.stack()
        # print(try_inspect[2].function)
        # print(try_inspect[2].code_context)
        # print("-------")
        # print(try_inspect[1].function)
        # print(try_inspect[1].code_context)
        # print('Vin: {} | {} --- Vout: {} | {}'.format(vmin,
        #                                               vmax,
        #                                               vmin_gained,
        #                                               vmax_gained))
        # print(" ***** --------- ********  ")
        # print("\n")
        # print("\n")
        # audio_float32 = (outmax - outmin)*(audio_float32 - vmin)/(vmax - vmin) \
        #     + outmin
        return audio_gained

    def norm_others_float32(self, audio_float32, gain_value, outmin, outmax):
        """
        Normalize float32 audio with the gain value provided
        """
        if audio_float32.dtype.kind != 'f':
            raise TypeError("'dtype' must be a floating point type")

        vmin = audio_float32.min()
        vmax = audio_float32.max()

        audio_gained = (outmax - outmin)*(audio_float32 - vmin)/(vmax - vmin) \
            + outmin

        audio_gained = audio_gained*gain_value

        vmin_gained = audio_gained.min()
        vmax_gained = audio_gained.max()

        nm_sum = np.sum(audio_float32)
        if np.isnan(nm_sum):
            try_inspect = inspect.stack()
            print(try_inspect[2].function)
            print(try_inspect[2].code_context)
            print("-------")
            print(try_inspect[1].function)
            print(try_inspect[1].code_context)
            print('Vin: {} | {} --- Vout: {} | {}'.format(vmin, 
                                                          vmax,
                                                          vmin_gained,
                                                          vmax_gained))
            print(" ***** --------- ********  ")
            pdb.set_trace()
        
        nm_sum = np.sum(audio_gained)
        if np.isnan(nm_sum):
            try_inspect = inspect.stack()
            print(try_inspect[2].function)
            print(try_inspect[2].code_context)
            print("-------")
            print("Audio gained")
            print(try_inspect[1].function)
            print(try_inspect[1].code_context)
            print('Vin: {} | {} --- Vout: {} | {}'.format(vmin, 
                                                          vmax,
                                                          vmin_gained,
                                                          vmax_gained))
            print(" ***** --------- ********  ")
            pdb.set_trace()



        return audio_gained

    def conv_2_int16(self, audio_float32, gain_value=1):
        """
        Converts float32 audio to int16 using
        the int16 min and max values by default
        """
        if audio_float32.dtype.kind != 'f':
            raise TypeError("'dtype' must be a floating point type")

        outmin = int(-32768*gain_value)
        outmax = int(32768*gain_value)

        vmin = audio_float32.min()
        vmax = audio_float32.max()

        audio_int16 = (outmax - outmin)*(audio_float32 - vmin)/(vmax - vmin) + outmin
        audio_int16 = audio_int16.astype('int16')
        return audio_int16

    def audio_mod(self, signal, gain_value, offset_value,
                  length_current_audio, outmin_current, outmax_current):
        """
        Modifies the signal with a gain_value (percentage) and
        offset_value(percentage) and converts output to int16
        """
        global counter_small

        signal_length = signal.shape[0]
        signal_offset = np.zeros_like(signal)
        others_current_audio = np.zeros((length_current_audio),
                                        dtype='float32')

    
        factor_length = np.min([length_current_audio, signal_length])
        
        # Calculate the offset factors at the start and end
        factor1 = int(factor_length*((abs(offset_value) - offset_value)/2))
        factor2 = int(factor_length*((abs(offset_value) + offset_value)/2))

        # Apply the offset factors
        signal_offset[factor1:(signal_length - factor2)] = \
            signal[factor2:(signal_length - factor1)]

        # Trim offset signal to the real length of the audio
        if signal_length > length_current_audio:
            others_current_audio = signal_offset[0:length_current_audio]
        else:
            others_current_audio[0:signal_length] = signal_offset
        
        if np.sum(others_current_audio) == 0:
            print("Offset failed!")
            pdb.set_trace()

        # Apply gain value and convert to required output format
        signal_offset_norm  = self.norm_others_float32(others_current_audio,
                                                  gain_value = gain_value,
                                                  outmin = outmin_current,
                                                  outmax = outmax_current)

        audio_sum = np.sum(signal_offset_norm)
        if audio_sum == 0:
            if factor1 >= length_current_audio:
                counter_small = counter_small + 1
                print("small audio encountered: counter {}".format(counter_small))
            else:
                print('Cero was found. Signal_offset {}. Factor {} - {}'.format(offset_value,
                                                                              factor1,
                                                                              factor2,))
                print('INDEXS signal_offset {} - {}. signal {} - {}'.format(factor1,
                                                                     (signal_length - factor2),
                                                                      factor2,
                                                                     (signal_length - factor1)))


        if np.isnan(audio_sum):
            print("NaN found in Noise " + str(offset_value))

            pdb.set_trace()

        return signal_offset_norm

    def noise_mod(self, noise, gain_value, length_current_audio,
                  outmin_current, outmax_current):
        """
        Modifies the signal with a gain_value (percentage) and
        offset_value(percentage) and converts output to int16
        """

        # Calculate the offset factors at the start
        noise_length = noise.shape[0]
        noise_current_audio = np.zeros((length_current_audio), dtype='float64')

        # Accomodate noise audios within the signal audio length
        if noise_length > length_current_audio:
            noise_current_audio = noise[0:length_current_audio]
        else:
            noise_current_audio[0:noise_length] = noise

        # Apply gain value and convert to required output format
        signal_offset_norm  = self.norm_others_float32(noise_current_audio,
                                          gain_value = gain_value,
                                          outmin = outmin_current,
                                          outmax = outmax_current)

        sum_noise = np.sum(signal_offset_norm)
        if np.isnan(sum_noise):
            print("NaN found in Noise")
            pdb.set_trace()

        return signal_offset_norm

    def sim_single_signal(self, input_signal, position=0, indx=0):
        """
        Pyroomacoustics simulation with 3 random other audios
        from the same x_data + 1 noise from AudioSet
        """

        length_current_audio = len(input_signal)
        outmin_current = input_signal.min()
        outmax_current = input_signal.max()

        # Load others audios
        indx_others_1 = random.randint(0, len(self.x_data)-1)
        indx_others_2 = random.randint(0, len(self.x_data)-1)
        indx_others_3 = random.randint(0, len(self.x_data)-1)
        indx_noise_4 = random.randint(0, len(self.noise_data)-1)

        others_audio1 = self.x_data[indx_others_1, :].astype('float32')
        others_audio2 = self.x_data[indx_others_2, :].astype('float32')
        others_audio3 = self.x_data[indx_others_3, :].astype('float32')
        noise_audio4 = self.noise_data[indx_noise_4].astype('float32')
        # noise_audio4 = self.noise_data[indx_noise_4, :].astype('float32')


        others_audio1 = np.trim_zeros(others_audio1)
        others_audio2 = np.trim_zeros(others_audio2)
        others_audio3 = np.trim_zeros(others_audio3)
        noise_audio4 = np.trim_zeros(noise_audio4)


        offset_value1 = self.gen_random_on_range(-0.4, 0.4)
        offset_value2 = self.gen_random_on_range(-0.4, 0.4)
        offset_value3 = self.gen_random_on_range(-0.4, 0.4)

        gain_value1 = self.gen_random_on_range(0.1, 0.2)
        gain_value2 = self.gen_random_on_range(0.05, 0.11)
        gain_value3 = self.gen_random_on_range(0.05, 0.1)
        gain_value4 = self.gen_random_on_range(0.08, 0.11)


        audio_offset1 = self.audio_mod(others_audio1, gain_value1,
                                       offset_value1, length_current_audio,
                                       outmin_current, outmax_current)
        audio_offset2 = self.audio_mod(others_audio2, gain_value2,
                                        offset_value2, length_current_audio,
                                        outmin_current, outmax_current)
        audio_offset3 = self.audio_mod(others_audio3, gain_value3,
                                        offset_value3, length_current_audio,
                                        outmin_current, outmax_current)
        audio_offset4 = self.noise_mod(noise_audio4, gain_value4,
                                        length_current_audio,
                                        outmin_current, outmax_current)

        audio_original = input_signal[0:length_current_audio]

        # Create 3D room and add sources
        room = pra.ShoeBox(self.room_cfg[0],
                           fs=fs,
                           absorption=abs_coeff,
                           max_order=12)

        src_dict = self.room_cfg[2]

        room.add_source(src_dict["src_{}".format(i_list[position])],
                        signal=audio_original)
        room.add_source(src_dict["src_{}".format(i_list[position-3])],
                        signal=audio_offset1)
        room.add_source(src_dict["src_{}".format(i_list[position-2])],
                        signal=audio_offset2)
        room.add_source(src_dict["src_{}".format(i_list[position-1])],
                        signal=audio_offset3)
        room.add_source(src_dict["src_{}".format(i_list[position])],
                        signal=audio_offset4)

        # Define microphone array
        mic_dict = self.room_cfg[1]
        R = np.c_[mic_dict["mic_0"], mic_dict["mic_0"]]
        room.add_microphone_array(pra.MicrophoneArray(R, room.fs))

        # Compute image sources
        room.image_source_model()
        room.simulate()

        # Simulate audio
        raw_sim_audio = room.mic_array.signals[0, :]

        sum_noise = np.sum(raw_sim_audio)
        if np.isnan(sum_noise):
            print("NaN found after Pyroom")
            pdb.set_trace()

        # Convert to required output format
        if self.float_flag:
            sim_audio = raw_sim_audio
            # sim_audio = self.n32(raw_sim_audio)
        else:
            sim_audio = self.conv_2_int16(raw_sim_audio)


        if indx%1000 == 0:
            print("{} -- {}. {} {} {}, noise {}. Len {} sim {}".format(indx,
                                                                       self.ds_name,
                                                                        indx_others_1,
                                                                        indx_others_2,
                                                                        indx_others_3,
                                                                        indx_noise_4,
                                                                        length_current_audio,
                                                                        len(sim_audio)))
            if position != 0:
                print("src_{} | src_{} src_{} src_{}".format(i_list[position],
                                                              i_list[position-3],
                                                              i_list[position-2],
                                                              i_list[position-1]))

        return sim_audio

    def sim_dataset(self, position=0):
        # global counter_small
        prev_time = time.process_time()
        for indx in range(0, self.x_data.shape[0]):
            single_signal = self.x_data[indx, :]
            single_signal_trimmed = np.trim_zeros(single_signal)

            if single_signal_trimmed.dtype.kind != 'f':
                raise TypeError("'dtype' must be a floating point type")
                
                
            single_signal_trimmed = librosa.effects.time_stretch(single_signal_trimmed, 1.1)

            single_x_DA = self.sim_single_signal(single_signal_trimmed
                                                 .astype('float32'),
                                                 position,
                                                 indx)


            single_x_DA_trimmed = self.eliminate_noise_start_ending(single_x_DA, 0.00001)
            self.x_data_DA.append(single_x_DA_trimmed)

            len_trim_sim = len(single_x_DA) - len(single_x_DA_trimmed)
            len_extra_sim = len(single_x_DA) - len(single_signal_trimmed)

            current_percentage = 100*(self.num_ite/self.num_total)

            if indx%100 == 0:
                # print('{} - Len {}, ExSim {}, Trm {} - {} - {:.2f}%'.format(indx,
                #                                         len(single_signal_trimmed),
                #                                         len_extra_sim,
                #                                         len_trim_sim,
                #                                         self.num_ite,
                #                                         current_percentage))

                current_time_100a = time.process_time()
                time_100a = current_time_100a - prev_time
                print('DA{}: {} - {} - {:.2f}% | time for 100 audios: {:.2f}'.format(self.DA_number,
                                                                        indx,
                                                                        self.num_ite,
                                                                        current_percentage,
                                                                        time_100a))
                prev_time = current_time_100a

            self.num_ite += 1

        print("These number of small audios:" + str(counter_small))
        return self.x_data_DA, self.num_ite
