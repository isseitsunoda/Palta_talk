import re
import random
from analyzer import *

class Markov:
    def make(self):
        # ログファイルを読み込む
        filename = 'data/log.txt'
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
        # プロンプトの文字列を取り除く
        text = re.sub('> ', '', text)
        text = re.sub('>', '', text)
        text = re.sub(
            'Ptna:Repeat|Ptna:Random|Ptna:Pattern|Ptna:Template|Ptna:Markov',
            '',
            text)
        # タイムスタンプの部分を取り除く
        text = re.sub('Ptna System Dialogue Log:.*\n', '', text)
        # 空白行が含まれていると\n\nが続くので\n１つにする
        text = re.sub('\n\n', '\n', text)
        # ログファイルの文章を形態素に分解してリストににする
        wordlist = parse(text)

    # マルコフ辞書の作成
        markov = {}
        p1 = ''
        p2 = ''
        p3 = ''
        for word in wordlist:
            # p1, p2, p3のすべてに値が格納されているか
            if p1 and p2 and p3:
                # markovに(p1, p2, p3)キーが存在するか
                if (p1, p2, p3) not in markov:
                    # なければキー：値のペアを追加
                    markov[(p1, p2, p3)] = []
            # キーのリストにサフィックスを追加（重複あり）
                markov[(p1, p2, p3)].append(word)
            # 3つのプレフィックスの値を置き換える
            p1, p2, p3 = p2, p3, word

        # マルコフ辞書から文章を作りだす
        count = 0
        sentence = ''
        # markovのキーをランダムに抽出し、プレフィックス1～3に代入
        p1, p2, p3 = random.choice(list(markov.keys()))
        while count < len(wordlist):
            # キーが存在するかチェック
            if ((p1, p2, p3) in markov) == True:
                # 文章にする単語を取得
                tmp = random.choice(markov[(p1, p2, p3)])
                # 取得した単語をsentenceに追加
                sentence += tmp
            # 3つのプレフィックスの値を置き換える
            p1, p2, p3 = p2, p3, tmp
            count += 1

        # 閉じ括弧を削除
        sentence = re.sub('」', '', sentence)
        # 開き括弧を削除
        sentence = re.sub('「', '', sentence)

        # 生成した文章を戻り値として返す
        return sentence
