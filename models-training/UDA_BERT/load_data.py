# Copyright 2019 SanghunYun, Korea University.
# (Strongly inspired by Dong-Hyun Lee, Kakao Brain)
# 
# This file has been modified by SanghunYun, Korea Univeristy.
# Little modification at Tokenizing, AddSpecialTokensWithTruncation, TokenIndexing
# and CsvDataset, load_data has been newly written.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from transformers import BertTokenizer

import ast
import csv
import itertools

import pandas as pd    # only import when no need_to_preprocessing
from tqdm import tqdm

import torch
from torch.utils.data import Dataset, DataLoader

from utils import tokenization
from utils.utils import truncate_tokens_pair
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, AlbertTokenizer, AlbertForSequenceClassification


CSV_FILE = 'sup.csv'
CSV_FILE_AUG = 'unsup.csv'
Y_COLUMN = 'label'
Y_COLUMN_AUG = 'new_text'
X_COLUMN = 'text'
X_COLUMN_AUG = 'new_text'
SPLIT_COLUMN = 'split'

class CsvDataset(Dataset):
    labels = None
    def __init__(self, file, need_prepro, pipeline, max_len, mode, d_type):
        Dataset.__init__(self)
        self.cnt = 0

        # need preprocessing
        if need_prepro:
            with open(file, 'r', encoding='utf-8') as f:
                lines = csv.reader(f, delimiter='\t', quotechar='"')

                # supervised dataset
                if d_type == 'sup':
                    # if mode == 'eval':
                        # sentences = []
                    data = []

                    for instance in self.get_sup(lines):
                        # if mode == 'eval':
                            # sentences.append([instance[1]])
                        for proc in pipeline:
                            instance = proc(instance, d_type)
                        data.append(instance)

                    self.tensors = [torch.tensor(x, dtype=torch.long) for x in zip(*data)]
                    # if mode == 'eval':
                        # self.tensors.append(sentences)

                # unsupervised dataset
                elif d_type == 'unsup':
                    data = {'ori':[], 'aug':[]}
                    for ori, aug in self.get_unsup(lines):
                        for proc in pipeline:
                            ori = proc(ori, d_type)
                            aug = proc(aug, d_type)
                        self.cnt += 1
                        # if self.cnt == 10:
                            # break
                        data['ori'].append(ori)    # drop label_id
                        data['aug'].append(aug)    # drop label_id
                    ori_tensor = [torch.tensor(x, dtype=torch.long) for x in zip(*data['ori'])]
                    aug_tensor = [torch.tensor(x, dtype=torch.long) for x in zip(*data['aug'])]
                    self.tensors = ori_tensor + aug_tensor
        # already preprocessed
        else:
            f = open(file, 'r', encoding='utf-8')
            data = pd.read_csv(f, sep='\t')

            # supervised dataset
            if d_type == 'sup':
                # input_ids, segment_ids(input_type_ids), input_mask, input_label
                input_columns = ['input_ids', 'input_type_ids', 'input_mask', 'label_ids']
                self.tensors = [torch.tensor(data[c].apply(lambda x: ast.literal_eval(x)), dtype=torch.long)    \
                                                                                for c in input_columns[:-1]]
                self.tensors.append(torch.tensor(data[input_columns[-1]], dtype=torch.long))
                
            # unsupervised dataset
            elif d_type == 'unsup':
                input_columns = ['ori_input_ids', 'ori_input_type_ids', 'ori_input_mask',
                                 'aug_input_ids', 'aug_input_type_ids', 'aug_input_mask']
                self.tensors = [torch.tensor(data[c].apply(lambda x: ast.literal_eval(x)), dtype=torch.long)    \
                                                                                for c in input_columns]
                
            else:
                raise "d_type error. (d_type have to sup or unsup)"

    def __len__(self):
        # return self.tensors[0].size(0)
        return 5

    def __getitem__(self, index):
        return tuple(tensor[index] for tensor in self.tensors)

    def get_sup(self, lines):
        raise NotImplementedError

    def get_unsup(self, lines):
        raise NotImplementedError


class Pipeline():
    def __init__(self):
        super().__init__()

    def __call__(self, instance):
        raise NotImplementedError


class Tokenizing(Pipeline):
    def __init__(self, preprocessor, tokenize):
        super().__init__()
        self.preprocessor = preprocessor
        self.tokenize = tokenize

    def __call__(self, instance, d_type):
        label, text_a, text_b = instance
        
        label = self.preprocessor(label) if label else None
        tokens_a = self.tokenize(self.preprocessor(text_a))
        tokens_b = self.tokenize(self.preprocessor(text_b)) if text_b else []

        return (label, tokens_a, tokens_b)


class AddSpecialTokensWithTruncation(Pipeline):
    def __init__(self, max_len=512):
        super().__init__()
        self.max_len = max_len
    
    def __call__(self, instance, d_type):
        label, tokens_a, tokens_b = instance

        # -3 special tokens for [CLS] text_a [SEP] text_b [SEP]
        # -2 special tokens for [CLS] text_a [SEP]
        _max_len = self.max_len - 3 if tokens_b else self.max_len - 2
        truncate_tokens_pair(tokens_a, tokens_b, _max_len)

        # Add Special Tokens
        tokens_a = ['[CLS]'] + tokens_a + ['[SEP]']
        tokens_b = tokens_b + ['[SEP]'] if tokens_b else []

        return (label, tokens_a, tokens_b)


class TokenIndexing(Pipeline):
    def __init__(self, indexer, labels, max_len=512):
        super().__init__()
        self.indexer = indexer # function : tokens to indexes
        # map from a label name to a label index
        self.label_map = {name: i for i, name in enumerate(labels)}
        self.max_len = max_len

    def __call__(self, instance, d_type):
        label, tokens_a, tokens_b = instance

        input_ids = self.indexer(tokens_a + tokens_b)
        segment_ids = [0]*len(tokens_a) + [1]*len(tokens_b) # type_ids
        input_mask = [1]*(len(tokens_a) + len(tokens_b))
        label_id = self.label_map[label] if label else None

        # zero padding
        n_pad = self.max_len - len(input_ids)
        input_ids.extend([0]*n_pad)
        segment_ids.extend([0]*n_pad)
        input_mask.extend([0]*n_pad)

        if label_id != None:
            return (input_ids, segment_ids, input_mask, label_id)
        else:
            return (input_ids, segment_ids, input_mask)


def dataset_class(task):
    table = {'imdb': IMDB}
    return table[task]


class IMDB(CsvDataset):
    labels = ('0', '1')
    def __init__(self, file, need_prepro, pipeline=[], max_len=128, mode='train', d_type='sup'):
        super().__init__(file, need_prepro, pipeline, max_len, mode, d_type)

    def get_sup(self, lines):
        for line in itertools.islice(lines, 0, None):
            yield line[7], line[6], []    # label, text_a, None
            # yield None, line[6], []

    def get_unsup(self, lines):
        for line in itertools.islice(lines, 0, None):
            yield (None, line[1], []), (None, line[2], [])  # ko, en


            # supervised dataset
            if d_type == 'sup':
                # input_ids, segment_ids(input_type_ids), input_mask, input_label
                input_columns = ['input_ids', 'input_type_ids', 'input_mask', 'label_ids']
                self.tensors = [torch.tensor(data[c].apply(lambda x: ast.literal_eval(x)), dtype=torch.long)    \
                                                                                for c in input_columns[:-1]]
                self.tensors.append(torch.tensor(data[input_columns[-1]], dtype=torch.long))
                
            # unsupervised dataset
            elif d_type == 'unsup':
                input_columns = ['ori_input_ids', 'ori_input_type_ids', 'ori_input_mask',
                                 'aug_input_ids', 'aug_input_type_ids', 'aug_input_mask']
                self.tensors = [torch.tensor(data[c].apply(lambda x: ast.literal_eval(x)), dtype=torch.long)    \
                                                                                for c in input_columns]



class HateDataset(torch.utils.data.Dataset):
    def __init__(self, d_type='sup'):
        self.d_type = d_type
        if self.d_type == 'sup':
            data = pd.read_csv(CSV_FILE, sep=',')
            data = data.sample(frac=1).reset_index(drop=True)
            n = data.shape[0]
            data = data.dropna()
            data[X_COLUMN] = data[X_COLUMN] 
            # data = data[[X_COLUMN, Y_COLUMN]]
            data[Y_COLUMN]=data[Y_COLUMN].apply(lambda x: 1 if x >= 0.5 else 0)
            data[Y_COLUMN] = data[Y_COLUMN].values.astype(int)

        else:
            data = pd.read_csv(CSV_FILE_AUG, sep=',')
            data = data.sample(frac=1).reset_index(drop=True)
            n = data.shape[0]
            data = data.dropna()
            # data[Y_COLUMN_AUG]=data[Y_COLUMN_AUG].apply(lambda x: 1 if x >= 0.5 else 0)
            # data[Y_COLUMN_AUG] = data[Y_COLUMN_AUG].values.astype(int)

        if self.d_type == 'sup':
            train_labels = list(data[data[SPLIT_COLUMN] == 0][Y_COLUMN].values)
            train_texts = list(data[data[SPLIT_COLUMN] == 0][X_COLUMN].values)

            test_labels = list(data[data[SPLIT_COLUMN] == 1][Y_COLUMN].values)
            test_texts = list(data[data[SPLIT_COLUMN] == 1][X_COLUMN].values)

        else:
            train_texts = list(data[X_COLUMN].values)
            train_texts_aug = list(data[X_COLUMN_AUG])

        self.n = data.shape[0]


        
        #tokenizer = AlbertTokenizer.from_pretrained('textattack/albert-base-v2-SST-2')
        MODEL_PATH = "dkleczek/bert-base-polish-uncased-v1"
        tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
        self.encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=100)
        if self.d_type == 'unsup':
            self.encodings_aug = tokenizer(train_texts_aug, truncation=True, padding=True, max_length=100)
        if self.d_type == 'sup':
            self.labels = train_labels
        

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.d_type == 'sup':
            sup_item = {}
            sup_item['label_ids'] = torch.tensor(self.labels[idx])
            sup_item['input_ids'] = item['input_ids']
            sup_item['input_type_ids'] = item['token_type_ids']
            sup_item['input_mask'] = item['attention_mask']
            item = (sup_item['input_ids'], sup_item['input_type_ids'], sup_item['input_mask'], sup_item['label_ids'])
            
        else:
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item_aug = {key: torch.tensor(val[idx]) for key, val in self.encodings_aug.items()}
            unsup_item = {}
            unsup_item['ori_input_ids'] = item['input_ids']
            unsup_item['aug_input_ids'] = item_aug['input_ids']
            unsup_item['ori_input_type_ids'] = item['token_type_ids']
            unsup_item['aug_input_type_ids'] = item_aug['token_type_ids']
            unsup_item['ori_input_mask'] = item['attention_mask']
            unsup_item['aug_input_mask'] = item_aug['attention_mask']
            item = (unsup_item['ori_input_ids'], unsup_item['ori_input_type_ids'], unsup_item['ori_input_mask'], unsup_item['ori_input_ids'], unsup_item['ori_input_type_ids'], unsup_item['ori_input_mask'])
        return item

    def __len__(self):
        return self.n


class load_data:
    def __init__(self, cfg):
        self.cfg = cfg

        self.TaskDataset = dataset_class(cfg.task)
        self.pipeline = None
        if cfg.need_prepro:
            tokenizer = tokenization.FullTokenizer(vocab_file=cfg.vocab, do_lower_case=cfg.do_lower_case)
            self.pipeline = [Tokenizing(tokenizer.convert_to_unicode, tokenizer.tokenize),
                        AddSpecialTokensWithTruncation(cfg.max_seq_length),
                        TokenIndexing(tokenizer.convert_tokens_to_ids, self.TaskDataset.labels, cfg.max_seq_length)]
        
        if cfg.mode == 'train':
            self.sup_data_dir = cfg.sup_data_dir
            self.sup_batch_size = cfg.train_batch_size
            self.shuffle = True
        elif cfg.mode == 'train_eval':
            self.sup_data_dir = cfg.sup_data_dir
            self.eval_data_dir= cfg.eval_data_dir
            self.sup_batch_size = cfg.train_batch_size
            self.eval_batch_size = cfg.eval_batch_size
            self.shuffle = True
        elif cfg.mode == 'eval':
            self.sup_data_dir = cfg.eval_data_dir
            self.sup_batch_size = cfg.eval_batch_size
            self.shuffle = False                            # Not shuffel when eval mode
        
        if cfg.uda_mode:                                    # Only uda_mode
            self.unsup_data_dir = cfg.unsup_data_dir
            self.unsup_batch_size = cfg.train_batch_size * cfg.unsup_ratio

    def sup_data_iter(self):
        # sup_dataset = self.TaskDataset(self.sup_data_dir, self.cfg.need_prepro, self.pipeline, self.cfg.max_seq_length, self.cfg.mode, 'sup')
        sup_dataset = HateDataset(d_type='sup')
        sup_data_iter = DataLoader(sup_dataset, batch_size=self.sup_batch_size, shuffle=self.shuffle)
        
        return sup_data_iter

    def unsup_data_iter(self):
        # unsup_dataset = self.TaskDataset(self.unsup_data_dir, self.cfg.need_prepro, self.pipeline, self.cfg.max_seq_length, self.cfg.mode, 'unsup')
        unsup_dataset = HateDataset(d_type='unsup')
        unsup_data_iter = DataLoader(unsup_dataset, batch_size=self.unsup_batch_size, shuffle=self.shuffle)
        print(len(unsup_data_iter), 'LEN')

        return unsup_data_iter

    def eval_data_iter(self):
        # eval_dataset = self.TaskDataset(self.eval_data_dir, self.cfg.need_prepro, self.pipeline, self.cfg.max_seq_length, 'eval', 'sup')
        eval_dataset = HateDataset(d_type='sup')
        eval_data_iter = DataLoader(eval_dataset, batch_size=self.eval_batch_size, shuffle=False)

        return eval_data_iter
