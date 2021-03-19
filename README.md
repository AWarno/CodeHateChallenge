# CodeHateChallenge

## Data augmentation
### EDA
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