
from utils_functions_tts_process import convert_numbers_text, detect_lang_transcr, select_people


old_transcr_path = '/home/luis/Dropbox/DATASETS_AUDIO/TTS_ENG_FEB05/Input_transcripts/input_txts/tts_feb05_5K_english.txt'

inter_transcr_path = old_transcr_path.split('/')[-1].split('.')[0] + '_intermediate' + '.txt'
print(inter_transcr_path)

current_lang = detect_lang_transcr(old_transcr_path)
people = select_people(current_lang)
'''Scan words in transcript. Keep a unique list. This will help me determine:
    - which words have typos
    - which words in english can be "rewritten" so they can be interpreted as
    spanish by phonemizer
    - which words are in english and this, which lines should be removed'''


'''Given a transcript and a list of characters to remove; iterate through all
the characters in the transcript and replace the unwanted characters with a
white space. After this, do a "clean up" of all possible-multiple white spaces
that are next to each other. Add an ID to the left of each line.'''


unwanted_chars = ['!', '"', "'", ',', '.', ';', '?' ]

replace_chars = [':', '-']

words2change = {'1st': 'first',
                '3rd': 'third',
                '0s': 'zeros',
                '+': ' plus ',
                '=': 'equal',
                '10th': 'tenth',
                '5th': 'fifth',
                '6th': 'sixth',
                '7th': 'seventh'}

chars2change = {}

#Iterate through each line in transcript
old_transcr = open(old_transcr_path, 'r')
new_transcr = open(inter_transcr_path, 'w')

vocabulary = []

idx = 0
for outer_idx, line in enumerate(old_transcr):
    #Iterate through each char in line. Replace unwanted chars with white space

    for char2replace in unwanted_chars:
        line = line.replace(char2replace, '')


    for char2replace in replace_chars:
        line = line.replace(char2replace, ' ')

    #Clean multiple white spaces that might be right next to each other
    #Also, clean spaces that might be at the end or beginning
    line = line.strip()

    words = line.split()
    for word in words:
        if word in list(words2change.keys()):
            # print(f'{idx}:{line}')
            idx += 1
            line = line.replace(word, words2change[word])

    line = convert_numbers_text(line)

    line += '\n'

    for char2replace in replace_chars:
        line = line.replace(char2replace, ' ')

    voc_words = line.strip().split('\t')[-1].split(' ')
    for voc_word in voc_words:
        if voc_word not in vocabulary:
            vocabulary.append(voc_word)

    new_transcr.write(str(outer_idx).zfill(4) + '\t' + line)

vocabulary = sorted(vocabulary)
new_transcr.close()
old_transcr.close()

#es-419


final_transcr_path = 'proto-transcript_' + old_transcr_path.split('/')[-1].split('.')[0] + '.txt'




# #Grab ID and name from each file listed in {err_txt_path}; then sort it
# err_txt_path = './list_of_errors_in_audios.txt'
# err_files = []
# err_txt = open(err_txt_path, 'r')
# for line in err_txt:
#     err_files.append(line.split('\t')[0].split('/')[-1])

# err_txt.close()
# err_files = sorted(err_files)

#Create dictionary of IDs as key and Transcript as value
f = open(inter_transcr_path, 'r')
lines = f.readlines()
f.close()

counter = 0
new_transcr = open(final_transcr_path, 'w')
for line in lines:
    ID, text = line.split('\t')
    for person in sorted(people):
        filename = f"{ID}_{person}.wav"
        # if filename not in err_files:
        new_transcr.write(f"{filename}\t{text}")
        counter += 1

new_transcr.close()
print(f"From {len(lines)*4} lines, {counter} were copied. The other ones "
      "had an error.")


# # # Here I should extract the dictionaries
