from eda_nlp.code.eda import eda


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

    def augment_text(self, sentence):
        aug_sentences = eda(sentence, alpha_sr=self.alpha_sr, alpha_ri=self.alpha_ri, alpha_rs=self.alpha_rs,
                            p_rd=self.alpha_rd,
                            num_aug=self.num_aug)
        return aug_sentences


if __name__=="__main__":
    augmenter = Augmenter()
    res = augmenter.augment_text("All black people should be slaves")
    print(res)