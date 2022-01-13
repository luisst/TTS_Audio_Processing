# Here I call the functions to clean the text
'''Given a transcript and a list of characters to remove; iterate through all
the characters in the transcript and replace the unwanted characters with a
white space. After this, do a "clean up" of all possible-multiple white spaces
that are next to each other. Add an ID to the left of each line.'''
old_transcr_path = './tts_transcripts_spanish_minitest.txt'
new_transcr_path = './spanish_cleaned_minitest_1.txt'

unwanted_chars = ['!', '"', "'", ',', '.', '?']

#Iterate through each line in transcript
old_transcr = open(old_transcr_path, 'r')
new_transcr = open(new_transcr_path, 'w')

for outer_idx, line in enumerate(old_transcr):
    #Iterate through each char in line. Replace unwanted chars with white space
    new_line = ''
    for idx, ch in enumerate(line):
        if ch in unwanted_chars:
            if ch == "'":
                new_line += ''
            else:
                new_line += ' '
        else:
            new_line += ch

    #Clean multiple white spaces that might be right next to each other
    #Also, clean spaces that might be at the end or beginning
    new_line = new_line.replace('    ', ' ')
    new_line = new_line.replace('   ', ' ')
    new_line = new_line.replace('  ', ' ')
    new_line = new_line.strip()
    new_line = new_line + '\n'

    new_transcr.write(str(outer_idx).zfill(4) + '\t' + new_line)

new_transcr.close()
old_transcr.close()


'''Given a transcript and a dictionary, iterate through the transcript and
replace the keys (numbers) in the dictionary with their respective values 
(written numbers).'''
old_transcr_path = './spanish_cleaned_minitest_1.txt'
new_transcr_path = './spanish_cleaned_minitest_2.txt'

#First, we will change the numbers with 3 digits
nums2changeI = {'255': 'doscientos cincuenta y cinco', '200': 'doscientos',
    '110': 'ciento diez', '100': 'cien', '46': 'cuarenta y seis',
    '34': 'treinta y cuatro', '33': 'treinta y tres',
    '32': 'treinta y dos', '30': 'treinta', '21': 'veintiuno', '16': 'dieciseis',
    '15': 'quince', '14': 'catorce', '12': 'doce', '11': 'once', '10': 'diez',
    '9': 'nueve', '8': 'ocho', '7': 'siete', '6': 'seis', '5': 'cinco',
    '4': 'cuatro', '3': 'tres', '2': 'dos', '1': 'uno', '0': 'cero'}

old_transcr = open(old_transcr_path, 'r')
lines = old_transcr.readlines()
old_transcr.close()

new_transcr = open(new_transcr_path, 'w')
for idx, line in enumerate(lines):
    ID, text = line.strip().split('\t')
    new_text = text
    words = text.split(' ')
    for word in words:
        if word in list(nums2changeI.keys()):
            new_text = new_text.replace(word, nums2changeI[word], 1)

    new_transcr.write(ID + '\t' + new_text + '\n')
new_transcr.close()

'''Scan words in transcript. Keep a unique list. This will help me determine:
    - which words have typos
    - which words in english can be "rewritten" so they can be interpreted as
    spanish by phonemizer
    - which words are in english and this, which lines should be removed'''


transcr_path = './spanish_cleaned_minitest_2.txt'

vocabulary = []
transcr = open(transcr_path, 'r')
for line in transcr:
    words = line.strip().split('\t')[-1].split(' ')
    for word in words:
        if word not in vocabulary:
            vocabulary.append(word)

vocabulary = sorted(vocabulary)

'''List English words given in 03a_get_vocabulary. Remove sentences that have
one of these words or that have a word without correction.'''

old_transcr_path = './spanish_cleaned_minitest_2.txt'
new_transcr_path = './spanish_cleaned_minitest_3.txt'
english_words = ['and', 'answers', 'app', 'apps', 'assassins', 'backboard',
    'background', 'ball', 'be', 'being', 'benny', 'between', 'bill', 'binary',
    'bits', 'black', 'board', 'brandon', 'brian', 'bus', 'center', 'christian',
    'click', 'column', 'creed', 'done', 'dont', 'draw', 'dress', 'field', 'do',
    'file', 'fine', 'five', 'flash', 'folders', 'for', 'four', 'frame', 'dollar',
    'frames', 'game', 'get', 'god', 'gonna', 'grey', 'guys', 'hashtag', 'pi', 
    'have', 'hex', 'hey', 'homework', 'hope', 'how', 'hundreds', 'image', 'umm',
    'im', 'in', 'ipad', 'its', 'jayden', 'joanna', 'joey', 'jordan', 'oho',
    'keyboard', 'know', 'kombat', 'like', 'line', 'lolly', 'loop', 'lost', 'um',
    'make', 'michael', 'might', 'mile', 'mind', 'miss', 'mister', 'module',
    'mouse', 'my', 'never', 'not', 'now', 'number', 'numbers', 'one', 'trente',
    'ones', 'open', 'paste', 'pixels', 'play', 'plus', 'project', 'python',
    'put', 'raspberry', 'remember', 'robots', 'row', 'run', 'scale', 'shentania',
    'show', 'sit', 'skeleton', 'sprite', 'switches', 'symbols', 'team', 'tens',
    'texas', 'three', 'toriyama', 'trip', 'trouble', 'tuition', 'two', 'up',
    'update', 'usa', 'wait', 'web', 'were', 'white', 'yeah', 'yellow', 'you']

old_transcr = open(old_transcr_path, 'r')
new_transcr = open(new_transcr_path, 'w')
counter = 0
for idx, line in enumerate(old_transcr):
    words = line.strip().split('\t')[-1].split(' ')
    save_line = True
    for word in words:
        if word in english_words:
            save_line = False
            break

    if save_line:
        new_transcr.write(line)
        counter += 1

old_transcr.close()
new_transcr.close()

print(f"In total, there were {idx+1} lines. {counter} didn't have english and"
      " were saved in the new transcript.")


'''Given a transcript and a dictionary, iterate through the transcript and
replace the keys with their values. These elements in the dictionary can be
considered "typos" that we are fixing.'''
old_transcr_path = './spanish_cleaned_minitest_3.txt'
new_transcr_path = './spanish_cleaned_minitest_4.txt'

replace_these = {'0000': 'cero cero cero cero', '00': 'cero cero',
    'f5': 'f cinco', 'Ahora': 'ahora', 'elque': 'el que',
    'espanol': 'español', 'manana': 'mañana', 'ok': 'okey',
    'okay': 'okey', 'stos': 'estos'}

#Others that were checked and didn't give any errors:
#ahhh, ahh, alguito, atenció, bianario, co, has, he, tambieé

old_transcr = open(old_transcr_path, 'r')
lines = old_transcr.readlines()
old_transcr.close()

counter = 0
new_transcr = open(new_transcr_path, 'w')
for idx, line in enumerate(lines):
    ID, text = line.strip().split('\t')
    words = text.split(' ')
    for word in words:
        if word in list(replace_these.keys()):
            text = text.replace(word, replace_these[word], 1)
            counter += 1

    new_transcr.write(ID + '\t' + text + '\n')

new_transcr.close()
print(f"Finished. {counter} words were edited.")

old_transcr_path = './spanish_cleaned_minitest_4.txt'
new_transcr_path = './spanish_cleaned_minitest_5.txt'

err_txt_path = './list_of_errors_in_audios.txt'
people = sorted(['Mia', 'Penelope', 'Lupe', 'Miguel'])

#Grab ID and name from each file listed in {err_txt_path}; then sort it
err_files = []
err_txt = open(err_txt_path, 'r')
for line in err_txt:
    err_files.append(line.split('\t')[0].split('/')[-1])

err_txt.close()
err_files = sorted(err_files)

#Create dictionary of IDs as key and Transcript as value
f = open(old_transcr_path, 'r')
lines = f.readlines()
f.close()

counter = 0
new_transcr = open(new_transcr_path, 'w')
for line in lines:
    ID, text = line.split('\t')
    for person in people:
        filename = f"{ID}_{person}_spanish.wav"
        if filename not in err_files:
            new_transcr.write(f"{filename}\t{text}")
            counter += 1

new_transcr.close()
print(f"From {len(lines)*4} lines, {counter} were copied. The other ones "
      "had an error.")


# Here I should extract the dictionaries
