# CodeHateChallenge

## Data augmentation

### Fast pipeline to augment data in any language
Pipeline can ba adopted easily to any language. 
Example pipeline for Polish language:
![Polish pipeline](data/pipeline.jpg)
### Scraping data (positive and negative examples)

The examples utterances (positive and negative) are scrap examples data from the page 
**https://pl.wiktionary.org/wiki/** based on list of offensive words. 
This process enables to increase the number of false-positive examples in the dataset.

Selenium is used to scrap the data. 

How to use:
```
python src/augment/scrap_wiki.py 
d = OffensiveDict("wiki_words2.json")
d.create_csv_with_utterances()
```

Example scraped sentences for word **pies**:
-  Czy to jest **pies** czy suka? " zool. Canis familiaris[1], zwierzę domowe; zob. też pies w Wikipedii" - not offencive example
-  **Psy** stoją na patrolu.,pies," slang. obraź. policjant[3], żandarm lub milicjant" - offencive example 



### EDA
EDA is a package used to augment data in English.  
GIT source: https://github.com/jasonwei20/eda_nlp.git 

Required to do before usage:
- install nltk
```
pip install -U nltk
```
- download wordnet
```
python
>>> import nltk; nltk.download('wordnet')
```
How to augment an English sentence:
```{python}
augmenter = Augmenter()
res = augmenter.augment_text("All black people should be slaves")
```
Example output:
```
['all black people totally should be slaves', 'all black be slaves', 'all black people totally should be slaves', 'all black people should be slaves', 'all black slaves should be people', 'all black people be slaves', 'atomic number all black people should be slaves', 'all shirley temple people should be slaves', 'all black the great unwashed should be slaves', 'all black people should be slaves']

```

### Custom back translation
Require to install:
```
pip install transformers
pip install neptune-client
pip install sentencepiece
pip install fairseq
pip install subword-nmt
```
How to use:
```
augmenter = Augmenter("polish_offensive_dict.json")
augmenter.back_translation("Kurwa, uchodźcy niszczą Polskę, jebane kozojebcy", first_lang="polish", second_lang="english")
```
Example result:
```
>>> Kurwa, uchodźcy niszczą Polskę, wy pierdolone kozie skurwiele.
```

## Models
### BERT UDA
Bert UDA architecture:
![Polish pipeline](data/bert_uda.png)

### Other models
- [detoxify ](https://github.com/unitaryai/detoxify)
- [transformers from huggingface](https://github.com/huggingface/transformers)
