from gensim.models import word2vec
import gensim
import pickle

model = gensim.models.KeyedVectors.load_word2vec_format('data/model.vec', binary=False)  # 毎回ロードすると時間がかかるので、pklにして時短
with open('data/model.pkl', 'wb') as f:
    pickle.dump(model, f)
