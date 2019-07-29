from responder import *
import requests
import json


# Responderクラスを継承するけど形態素解析結果を使わずに直接返答を作成するのでresponseメソッドはオーバーライドしない。
class TalkApiResponder(Responder):
    def __init__(self):
        self.key = 'DZZMqOW2hpzSQtMZRYxOeY9cbWzKn6LI'
        self.api = 'https://api.a3rt.recruit-tech.co.jp/talk/v1/smalltalk'

    def get(self,talking):
        url = self.api
        r = requests.post(url,{'apikey':self.key,'query':talking})
        data = json.loads(r.text)
        if data['status'] == 0:
            t = data['results']
            ret = t[0]['reply']
        else:
            ret = 'ダメダニホンゴワカラナイ' # 理解できませんでした。にしよかな
        return ret


talk = TalkApiResponder()
input = '男なの？'
print(talk.get(input))

