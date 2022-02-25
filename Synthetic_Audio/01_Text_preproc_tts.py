import re

# list of words to replace
old_transcr_path = '/home/luis/Dropbox/01_TTS_Audio_Processing/Synthetic_Audio/tts_feb05_5K_english.txt'
new_transcr_path = old_transcr_path.split('/')[-1].split('.')[0] + '_ttsCorrected' + '.txt'
print(new_transcr_path)


words2change = {" pwd ": "p w d",
                "aolme": "a ol me",
                " ls ": "l s",
                " cd ": "c d",
                " umm ": "",
                " mmm ": "",
                " y ": " wye ",
                " z ": " zee ",
                "mkdir": "m k dir",
                " 00 ": "0 0",
                " ff ": "f f",
                "\*": " times "}

# Iterate through each line in transcript
old_transcr = open(old_transcr_path, 'r')
new_transcr = open(new_transcr_path, 'w')

for idx, line in enumerate(old_transcr):
    if line == '\n':
        print(f'line in index {idx} is empty!')
        continue
    if '*' in line:
        str_2_log = f'{idx} - * found: {line}'
        print(str_2_log)
        line = line.replace('*', ' times ')
    line = line.strip()
    line = line.strip('\"')
    line += '\n'
    words = line.split()

    for word in words2change.keys():
        if bool(re.search(word, line)):
            line = line.replace(word, words2change[word])
            str_2_log = f'{idx} - {word}: {line}'
            # list_errors.append(f'{idx} : {str_2_log}')
            # print(str_2_log)
    new_transcr.write(line)

new_transcr.close()
old_transcr.close()

# store in list those lines with their cnt number and text BEFORE MODIF
