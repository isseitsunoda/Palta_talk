import re
import pickle

with open('Japanese_L-12_H-768_A-12_E-30_BPE/Japanese_L-12_H-768_A-12_E-30_BPE/vocab.txt', encoding='utf-8') as f:
    words = {w.rstrip().replace('#', '') for w in f.readlines()}

with open('dics/vocab', 'wb') as f:
    pickle.dump(words, f)
