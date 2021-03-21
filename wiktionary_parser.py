import json
import pickle


# path to wiktionary with scraped language dict
JSON_PATH = 'wiki.json'

# offensive_words_tags = ['contemptuous', 'slur', 'vulgar', 'derogatory']
OFFENSIVE_WORDS_TAGS = ['slur', 'vulgar', 'derogatory']


def main():
    wrong_words = dict()
    words_dict = set()
    for line in open(JSON_PATH, 'r'):
        word = json.loads(line)
        words_dict.add(word['word'])
        if 'senses' in word:
            for elem in word['senses']:
                if 'tags' in elem:
                    if any(x in OFFENSIVE_WORDS_TAGS for x in elem['tags']):
                        #wrong_words.append(word['word'])
                        wrong_words[word['word']] = {'pos': word['pos'], 'tags': elem['tags'], 'base_form': True}
                        
                        if 'inflection' in word:
                            for numb in word['inflection'][0]:
                                if numb.isnumeric() and len(word['inflection'][0][numb]) > 2:
                                    wrong_words[word['inflection'][0][numb]] = {'pos': word['pos'], 'tags': elem['tags']}

    with open("polish_offensive_dict.json", "w") as write_file:
        json.dump(wrong_words, write_file)

    pickle.dump(words_dict, open("polish_dict.p", "wb") )


if __name__ == '__main__':
    main()




