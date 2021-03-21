import csv
import json


class OffensiveDict:
    def __init__(self, path):
        with open(path) as f:
            self.offensive_dict = json.load(f)

    def create_csv_with_utterances(self):
        meanings_dict = {}
        for key in self.offensive_dict:
            meanings_dict[key] = {}
            if len(self.offensive_dict[key]["znaczenie"]) > 0:
                for example in self.offensive_dict[key]["znaczenie"]:
                    split_meanings = example.split("\n")
                    for meaning in split_meanings:
                        partitioned = meaning.partition(")")
                        meanings_dict[key][partitioned[0] + partitioned[1]] = partitioned[2]

        sentences = [["sentence", "word", "meaning"]]
        for key in self.offensive_dict:
            if len(self.offensive_dict[key]["przyk"]) > 0:
                for example in  self.offensive_dict[key]["przyk"]:
                    print(example)
                    split_example = example.replace("przykłady:", key).split("\n")[1:]
                    for sentence in split_example:
                        partitioned = sentence.partition(")")
                        if partitioned[0]+partitioned[1] in meanings_dict[key]:
                            sentences.append([partitioned[2], key,  meanings_dict[key][partitioned[0]+partitioned[1]]])
                        else:
                            sentences.append([partitioned[2], key, ""])
        with open("wiki_offensive_pl_utterancs.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(sentences)







if __name__=="__main__":
    d = OffensiveDict("wiki_words2.json")
    d.create_csv_with_utterances()
    print(d.offensive_dict)