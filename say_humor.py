import random
class HumorResponder:
    def __init__(self):
        self.humors = []
        with open('dics/humor.txt', encoding='utf-8') as f:
            self.humors = f.readlines()
        #print(self.humors)


    def say(self):
        return random.choice(self.humors)


if __name__ == "__main__":
    from paltaForm import *
    h = HumorResponder()
    s = h.say()
    print(s)
    text_to_speech(s)
