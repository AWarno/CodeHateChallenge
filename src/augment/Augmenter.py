from fairseq.models import BaseFairseqModel
import pickle
import spacy
import pl_core_news_sm

from src.augment.eda_nlp.code.eda import eda
from src.augment.offensive_dict import OffensiveDict

WORDS_PATH = '../../polish_dict.p'


class Augmenter:

    def __init__(self, path: str, num_aug=9, alpha_sr=0.1, alpha_ri=0.1, alpha_rs=0.1, alpha_rd=0.1):
        # number of augmented sentences to generate per original sentence
        self.num_aug = num_aug

        # how much to replace each word by synonyms
        self.alpha_sr = alpha_sr

        # how much to insert new words that are synonyms
        self.alpha_ri = alpha_ri

        # how much to swap words
        self.alpha_rs = 0.

        # how much to delete words
        self.alpha_rd = alpha_rd

        # polish words pickle
        with open(WORDS_PATH, 'rb') as handle:
            self.polish_words = pickle.load(handle)

        # spacy nlp lemmatizer for polish
        self.nlp = pl_core_news_sm.load()

        self.translator_eng_pl = BaseFairseqModel.from_pretrained(
            model_name_or_path="english-polish-conv",
            checkpoint_file="checkpoint_best.pt",
            data_name_or_path="english-polish-conv",
            tokenizer="moses",
            bpe="subword_nmt",
            bpe_codes="code",
            cpu=False
        )

        self.translator_eng_pl.to(torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))

        self.translator_pl_eng = BaseFairseqModel.from_pretrained(
            model_name_or_path="polish-english-conv",
            checkpoint_file="checkpoint_best.pt",
            data_name_or_path="polish-english-conv",
            tokenizer="moses",
            bpe="subword_nmt",
            bpe_codes="code",
            cpu=False
        )

        self.translator_pl_eng.to(torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))

        self.offensive_dict = OffensiveDict(path)

    # def _divide_by_offensive_words(self, sentence):
    #     sentence_split = sentence.split(" ")
    #     list_s = []
    #     substring = []
    #     for word in sentence_split:
    #         if word in OFFENSIVE_DICT:
    #             if len(substring) > 0:
    #                 list_s.append([" ".join(substring)])
    #                 substring = []
    #             list_s.append([word, "OFFENSIVE"])
    #         else:
    #             substring.append(word)
    #     if len(substring) > 0:
    #         list_s.append([" ".join(substring)])
    #     return list_s
    #
    # def augment_text(self, sentence, first_lang, second_lang='english'):
    #     sentence_list = [[sentence]]
    #     if first_lang == "polish":
    #         list_s = self._divide_by_offensive_words(sentence)
    #         print(list_s)
    #         sentence_list = [[self.translator_pl_eng.translate(sentences=part[0], beam=5)] if len(part) <= 1 else [
    #             self.translator_pl_eng.translate(sentences=part[0], beam=5), part[1]] for part in list_s]
    #     aug_sentences = [[eda(part[0], alpha_sr=self.alpha_sr, alpha_ri=self.alpha_ri, alpha_rs=self.alpha_rs,
    #                           p_rd=self.alpha_rd, num_aug=self.num_aug), part[1:] * (self.num_aug + 1)] for part in
    #                      sentence_list]
    #     combined_aug = []
    #     for i in range(len(aug_sentences[0][0])):
    #         combined_aug.append(
    #             [[part[0][i], part[1][i]] if len(part[1]) == len(aug_sentences[0][0]) else [part[0][i]] for part in
    #              aug_sentences])
    #     assert len(combined_aug) == len(aug_sentences[0][0])
    #
    #     result = []
    #     for sent_aug in combined_aug:
    #         n_sent_aug = []
    #         for part in sent_aug:
    #             if second_lang == "polish":
    #                 n_sent_aug.append(self.translator_eng_pl.translate(sentences=part[0], beam=5) if len(
    #                     part) <= 1 else "<" + self.translator_eng_pl.translate(sentences=part[0], beam=5) + " " + part[
    #                     1] + ">")
    #             else:
    #                 n_sent_aug.append(part[0] if len(part) <= 1 else "<" + part[0] + " " + part[1] + ">")
    #         result.append(" ".join(n_sent_aug).replace(".", "").replace("/", ""))
    #     return result

    def _divide_by_offensive_words(self, sentence):
        sentence_split = sentence.split(" ")
        new_sent = []
        for word in sentence_split:
            if word in self.offensive_dict.offensive_dict:
                new_sent.append("< "+word + " >")
            else:
                new_sent.append(word)

        return " ".join(new_sent)

    def is_word(self, word):
        if word in self.polish_words:
            return True
        else:
            return False

    def is_polish_sentence(seq, tresh=0.7):
        seq_len = len(seq.split(' '))
        lemmas = self.nlp(seq)
        correct_words = [y for y in lemmas if self.is_word(y.lemma_)]
        if len(correct_words / seq_len) < tresh:
            return False
        return True
        
        
        

    def augment_text(self, sentence, first_lang, second_lang='english'):
        if first_lang == "polish":
            new_sent = self._divide_by_offensive_words(sentence)
            sentence = self.translator_pl_eng.translate(sentences=new_sent, beam=5)
            print(new_sent)

            print(sentence)
        aug_sentences = eda(sentence, alpha_sr=self.alpha_sr, alpha_ri=self.alpha_ri, alpha_rs=self.alpha_rs,
                              p_rd=self.alpha_rd, num_aug=self.num_aug)

        if second_lang == "polish":
            print(aug_sentences)
            return [self.translator_eng_pl.translate(sentences=part, beam=5) for part in aug_sentences]
        return aug_sentences

    def back_translation(self, sentence, first_lang="polish", second_lang="english"):
        if first_lang == "polish" and second_lang == "english":
            translated = self.translator_pl_eng.translate(sentences=sentence, beam=5)
            return self.translator_eng_pl.translate(sentences=translated, beam=5)


if __name__ == "__main__":
    augmenter = Augmenter("../../polish_offensive_dict.json")
    res = augmenter.augment_text("kebab Tomasz Lis jest Żydem i murzynem", "polish", second_lang="polish")
    print(augmenter.is_polish_sentence("cza cza cza cza"))
    # print(res)
