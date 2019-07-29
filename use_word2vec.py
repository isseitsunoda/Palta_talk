import gensim
import pickle as pkl
from mpmath import mp, mpf
import MeCab
# from gensim.models import word2vec
import gensim
import numpy as np


class W2V:
    def __init__(self):
        # neologdを使うので流行語にも対応できるはず
        self.mecab = MeCab.Tagger(r'-d C:\neologd')
        self.mecab.parse('')
        #model = gensim.models.KeyedVectors.load_word2vec_format('data/model.vec', binary=False)  # 毎回ロードすると時間がかかるので、pklにしたものをロードして時短
        with open('data/model.pkl', 'rb') as f:
            self.model = pkl.load(f)

    # テキストのベクトルを計算
    def get_vector(self, text):
        # sum_vec = np.zeros(200)
        sum_vec = np.zeros(300)  # ここが200のままだとsum_vec += model.wv[item.split('\t')[0]]の部分でbroadcastエラーになる。
        word_count = 0
        # python3.7.1だとparseToNodeメソッドでうまく形態素解析できないためparse()とsplitlines(), split()で書き直した
        node = self.mecab.parse(text).splitlines()
        print(node, '%%%%%%%%%%%%%%%%%%%%%%')
        for item in node:
            if item.split('\t')[0] == 'EOS':
                break
            field = item.split('\t')[1].split(',')[0]
            if field == '名詞' or field == '動詞' or field == '形容詞' or field == '感動詞':
                try:
                    sum_vec += self.model.wv[item.split('\t')[0]]
                except KeyError:  # 形態素解析した結果、未知の形で言葉がでてしまった場合の処理
                    sum_vec += np.random.rand(300)  # ほんとはネット検索して一番近そうな単語を取ってくるとかあるけど
                    print('形態素解析失敗')
                #print('$$$$$$$$$$$$$$$$$$$$$$$4', self.model.wv[item.split('\t')[0]], '&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
                word_count += 1
        if word_count == 0:
            return np.random.rand(300)
        print(text, (sum_vec / word_count), sep='||')
        return sum_vec / word_count

    # cos類似度を計算
    def cos_sim(self, v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    # softmaxで処理したものを確率分布に従ってチョイス
    def soft_max_choice(self, input, sentence_list):
        # 文章の類似度を計算
        simi = []
        for sentence in sentence_list:
            simi.append(self.cos_sim(self.get_vector(input), self.get_vector(sentence)))

        print(simi)

        # softmaxを計算
        exp_simi = []
        c = np.max(simi)
        mp.dps = 150
        for d in simi:
            # print(d, c, (d - c), np.exp(d - c))
            exp_simi.append(np.exp(d - c))

        sum = 0
        # print(exp_dots)
        for d in exp_simi:
            sum += mpf(d)

        softs = []
        for d in exp_simi:
            # print((mpf(d) / mpf(sum)), d, sum, sep='||', end='\n')
            softs.append(mpf(d) / mpf(sum))

        indexs = list(range(len(softs)))
        for index, soft in zip(indexs, softs):
            print(index, soft, sep='@')


        print(softs,exp_simi,sum,sep='||')
        return np.random.choice(indexs, p=softs)





if __name__ == "__main__":
    w2v = W2V()
    v1 = w2v.get_vector('昨日、お笑い番組を見た。')
    v2 = w2v.get_vector('昨夜、テレビで漫才をやっていた。')
    v3 = w2v.get_vector('昨日、公園に行った。')

    print(w2v.cos_sim(v1, v2))
    print(w2v.cos_sim(v1, v3))
