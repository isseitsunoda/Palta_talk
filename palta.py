from responder import *
from dictionary import *
from analyzer import *
import pickle
from use_word2vec import *


class Ptna:
    """パルタの本体クラス
    """

    def __init__(self, name):
        """Paltaオブジェクトの名前をnameに格納
        Responderオブジェクトを生成してresponderに格納

        :param name: Paltaオブジェクトの名前
        """
        self.name = name
        # Dictionaryを生成する
        self.dictionary = Dictionary()
        # Emotionを生成
        self.emotion = Emotion(self.dictionary)

        # RandomResponderを生成
        self.res_random = RandomResponder('Random', self.dictionary)
        # RepeatResponderを生成
        self.res_what = RepeatResponder('Repeat', self.dictionary)
        # PatternResponderを生成する
        self.res_pattern = PatternResponder('Pattern', self.dictionary)
        # TemplateResponderを生成する
        self.resp_template = TemplateResponder('Template', self.dictionary)
        # MarkovResponderを生成する
        self.resp_markov = MarkovResponder('Markov', self.dictionary)
        # TalkAPIResponderを生成する
        self.resp_api = TalkApiResponder('TalkAPI', self.dictionary)
        self.w2v = W2V()


    def dialogue_similarity(self, input):
        """
        応答オブジェクトのresponse()を呼び出して
        応答文字列を取得する
        その中から最も内積の値が大きなものを選び、返答候補とする

        :param input:ユーザーによって入力された文字列
        :return:応答文字列
        """
        # 機嫌値を更新
        self.emotion.update(input)
        # インプット文字列を解析
        parts = analyze(input)
        # print(parts)
        # print(self.emotion.mood)

        # 応答フレーズを複数生成
        resps = []
        resps.append(self.res_pattern)
        resps.append(self.resp_template)
        resps.append(self.res_random)
        resps.append(self.resp_markov)
        # res_whatについては未登録語が来たら使う
        #resps.append(self.res_what)
        resps.append(self.resp_api)

        sentences = []

        # 未知語が来た場合の処理
        for word, part in parts:
            # w2vの辞書を確認
            if word not in self.w2v.model.vocab:
                print('=======================未知単語=========================')
                # 学習メソッドを呼ぶ
                self.dictionary.study(input, parts)
                self.responder = self.res_what
                if keyword_check(part):
                    # 未知語がキーワードであればユーザーにたずねる
                    return self.responder.response(word, self.emotion.mood, parts)
                # 理解できなかったこととして文ごとユーザーにオウム返しでたずねる
                return self.responder.response(input, self.emotion.mood, parts)

        for resp in resps:
            sentences.append(resp.response(input, self.emotion.mood, parts))

        n = self.w2v.soft_max_choice(input, sentences)
        resp = sentences[n]

        for i, s in enumerate(sentences):
            print(i, s)
        self.responder = resps[n]

        # 学習メソッドを呼ぶ
        self.dictionary.study(input, parts)
        # 応答フレーズを返す
        return resp


    def save(self):
        """
        Dictionaryのsave()を呼ぶ中継メソッド
        """
        self.dictionary.save()

    def get_responder_name(self):
        """
        応答オブジェクトの名前を返す
        """
        return self.responder.name

    def get_name(self):
        """
        Ptnaオブジェクトの名前を返す
        """
        return self.name


class Emotion:
    """
    ピティナの感情モデル
    """
    # 期限値の上限/加減と回復値を設定
    MOOD_MIN = -15
    MOOD_MAX = 15
    MOOD_RECOVERY = 0.5

    def __init__(self, dictionary):
        """
        Dictionaryオブジェクトをdictionaryに格納
        機嫌値moodを0で初期化

        :param dictionary:Dictionaryオブジェクト
        """
        self.dictionary = dictionary
        # 機嫌値を保持するインスタンス変数
        self.mood = 0

    def update(self, input):
        """
        ユーザーからの入力をパラメータinputで受け取り
        パターン辞書にマッチさせて機嫌値を変動させる
        :param input: ユーザーからの入力
        """
        # パターン辞書の各行を繰り返しパターンマッチさせる
        for ptn_item in self.dictionary.pattern:
            # パターンマッチすればadjust_mood()で機嫌値を変動させる
            if ptn_item.match(input):
                self.adjust_mood(ptn_item.modify)
                break

        # 機嫌を徐々に戻す処理
        if self.mood < 0:
            self.mood += Emotion.MOOD_RECOVERY
        elif self.mood > 0:
            self.mood -= Emotion.MOOD_RECOVERY

    def adjust_mood(self, val):
        """
        機嫌値を増減する
        :param val: 機嫌変動値
        """
        # 機嫌値moodの値を機嫌変動値によって増減する
        self.mood += int(val)
        # MOOD_MAXとMOOD_MINと比較して、機嫌値が取り得る範囲に収める
        if self.mood > Emotion.MOOD_MAX:
            self.mood = Emotion.MOOD_MAX
        elif self.mood < Emotion.MOOD_MIN:
            self.mood = Emotion.MOOD_MIN

