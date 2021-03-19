from fairseq.models import BaseFairseqModel

from augment.eda_nlp.code.eda import eda
from src.augment.settings import PATH_MODEL_ENG_TO_PL


class Augmenter:

    def __init__(self, num_aug=9, alpha_sr=0.1, alpha_ri=0.1, alpha_rs=0.1, alpha_rd=0.1):
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

        # self.translator = BaseFairseqModel.from_pretrained(
        #     model_name_or_path=PATH_MODEL_ENG_TO_PL,
        #     checkpoint_file="checkpoint_best.pt",
        #     data_name_or_path=PATH_MODEL_ENG_TO_PL,
        #     tokenizer="moses",
        #     bpe="subword_nmt",
        #     bpe_codes="code",
        #     cpu=False
        # )

    def augment_text(self, sentence):
        aug_sentences = eda(sentence, alpha_sr=self.alpha_sr, alpha_ri=self.alpha_ri, alpha_rs=self.alpha_rs,
                            p_rd=self.alpha_rd,
                            num_aug=self.num_aug)
        return aug_sentences




if __name__=="__main__":
    augmenter = Augmenter()
    res = augmenter.augment_text("All black people should be slaves")
    print(res)