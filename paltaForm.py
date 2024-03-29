from palta import *
from datetime import datetime
import tkinter as tk
import tkinter.messagebox
from is_weather import *
from say_humor import *
import speech_recognition as sr
from gtts import gTTS
from mutagen.mp3 import MP3 as mp3
import pygame
import mmap
import time
import threading

""" グローバル変数の定義
"""
entry = None  # 入力エリアのオブジェクトを保持
response_area = None  # 応答エリアのオブジェクトを保持
lb = None  # ログ表示用リストボックスを保持
action = None  # 'オプション'メニューの状態を保持
ptna = Ptna('ptna')  # Ptnaオブジェクトを保持
on_canvas = None  # Canvasオブジェクトを保持
ptyna_images = []  # イメージを保持
log = []  # インプット文字列を保持
weather = WeatherResponder()  ##
humor = HumorResponder()  ##
question = 0  ##


##place = '' ##

def putlog(str):
    """ 対話ログをリストボックスに追加する関数
        @str  入力文字列または応答メッセージ
    """
    lb.insert(tk.END, str)
    # インプットと応答をリストlogに追加
    log.append(str + '\n')


def prompt():
    """ ピティナのプロンプトを作る関数
    """
    p = ptna.name
    if (action.get()) == 0:
        p += '：' + ptna.responder.name
    return p + '> '


def chagImg(img):
    """ 画像をセットする関数
    """
    canvas.itemconfig(
        on_canvas,
        image=ptyna_images[img]  # 表示するイメージを変更
    )


def change_looks():
    em = ptna.emotion.mood
    if -5 < em < 5:
        chagImg(0)
    elif -10 <= em <= -5:
        chagImg(1)
    elif -15 <= em < -10:
        chagImg(2)
    elif 5 <= em <= 15:
        chagImg(3)


def recognize_voice():
    r = sr.Recognizer()
    mic = sr.Microphone()
    print('聞いてるよ！')
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        return r.recognize_google(audio, language='ja-JP')
    except:
        response_area.configure(text='ごめんね、もう一回言って')
        text_to_speech('ごめんね、もう一回言って')
        return ''


def play_voice():
    print('発声開始')
    filename = 'data/tmp_voice.mp3'
    with open(filename) as f:
        m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    pygame.mixer.init(44100)
    pygame.mixer.music.load(m)  # 音源を読み込み # pygameは音声ファイルをcloseしないバグがあるので対応
    mp3_length = mp3(filename).info.length  # 音源の長さ取得
    pygame.mixer.music.play(1)  # 再生開始。1の部分を変えるとn回再生(その場合は次の行の秒数も×nすること)
    time.sleep(mp3_length)  # 再生開始後、音源の長さだけ待つ(0.25待つと誤差解消できたりする)
    pygame.mixer.music.stop()  # 音源の長さ待ったら再生停止
    m.close()


def text_to_speech(text):
    tts = gTTS(text=text, lang='ja')
    tts.save('data/tmp_voice.mp3'),
    play_voice()


def talk():
    """ 対話を行う関数
        ・Ptnaクラスのdialogue()を実行しsて応答メッセージを取得
        ・入力文字列およかわいいび応答メッセージをログに出力
    """
    global question
    value = entry.get()

    # 入力エリアが未入力の場合
    if not value:
        response_area.configure(text='なにかな？ 話してみて！')
        text_to_speech('なにかな？ 話してみて！')
        value = recognize_voice()
        print(value + 'a')

    if value == '天気予報' or value == '今日の天気':
        if question == 0:
            response_area.configure(text='どこの天気？')
            text_to_speech('どこの天気？')
            question = 1
            # 入力エリアをクリア
            entry.delete(0, tk.END)
    elif question == 1:
        response = weather.is_weather(value)
        response_area.configure(text=response)
        # text_to_speech(response)
        question = 0
        # 入力エリアをクリア
        entry.delete(0, tk.END)
    elif value == '何か面白いこと言って' or value == '面白いこと言って' or value == '面白いこと話して' or value == '面白いこと':
        response = humor.say()
        response_area.configure(text=response)
        # 入力エリアをクリア
        entry.delete(0, tk.END)
        thread_1 = threading.Thread(target=text_to_speech(response))
        thread_1.start()
    # 入力されていたら対話オブジェクトを実行
    elif value != '':
        # 入力文字列を引数にしてdialogue()の結果を取得
        response = ptna.dialogue_similarity(value)
        # 応答メッセージを表示
        response_area.configure(text=response)
        # 応答メッセージを読み上げ
        text_to_speech(response)
        # 入力文字列引数にしてputlog()を呼ぶ
        putlog('> ' + value)
        # 応答メッセージを引数にしてputlog()を呼ぶ
        putlog(prompt() + response)
        # 入力エリアをクリア
        entry.delete(0, tk.END)

    change_looks()  # 画像チェンジ


def writeLog():
    """ ログファイルに辞書を更新した日時を記録
    """
    # ログを作成
    now = 'Ptna System Dialogue Log: ' + datetime.now().strftime(
        '%Y-%m-%d %H:%m::%S' + '\n')
    log.insert(0, now)
    # ログファイルへの書き込み
    with open('log.txt', 'a', encoding='utf_8') as f:
        f.writelines(log)


# =================================================
# 画面を描画する関数
# =================================================

def run():
    # グローバル変数を使用するための記述
    global entry, response_area, lb, action, canvas, on_canvas, ptyna_images

    # メインウィンドウを作成
    root = tk.Tk()
    # ウィンドウのサイズを設定
    root.geometry('880x560')
    # ウィンドウのタイトルを設定
    root.title('Intelligent Agent : ')
    # フォントの用意
    font = ('Helevetica', 14)
    font_log = ('Helevetica', 11)

    def callback():
        """ 終了時の処理
        """
        # メッセージボックスの[OK]ボタンクリック時の処理
        if tkinter.messagebox.askyesno(
                'Quit?', '辞書を更新してもいい?'):
            ptna.save()  # 記憶メソッド実行
            writeLog()  # ログの保存
            root.destroy()
        # [キャンセル]ボタンクリック
        else:
            root.destroy()

    root.protocol('WM_DELETE_WINDOW', callback)

    # メニューバーの作成
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    # 「ファイル」メニュー
    filemenu = tk.Menu(menubar)
    menubar.add_cascade(label='ファイル', menu=filemenu)
    filemenu.add_command(label='閉じる', command=callback)
    # 「オプション」メニュー
    action = tk.IntVar()
    optionmenu = tk.Menu(menubar)
    menubar.add_cascade(label='オプション', menu=optionmenu)
    optionmenu.add_radiobutton(
        label='Responderを表示',  # アイテム名
        variable=action,  # 選択時の値を格納するオブジェクト
        value=0  # actionの値を0にする
    )
    optionmenu.add_radiobutton(
        label='Responderを表示しない',  # アイテム名
        variable=action,  # 選択時の値を格納するオブジェクト
        value=1  # actionの値を0にする
    )

    # キャンバスの作成
    canvas = tk.Canvas(
        root,  # 親要素をメインウィンドウに設定
        width=500,  # 幅を設定
        height=300,  # 高さを設定
        relief=tk.RIDGE,  # 枠線を表示
        bd=2  # 枠線の幅を設定
    )
    canvas.place(x=370, y=0)  # メインウィンドウ上に配置

    # イメージを用意
    ptyna_images.append(tk.PhotoImage(file="パルタ_talk.png"))
    ptyna_images.append(tk.PhotoImage(file="パルタ_empty.png"))
    ptyna_images.append(tk.PhotoImage(file="パルタ_angry.png"))
    ptyna_images.append(tk.PhotoImage(file="パルタ_happy.png"))

    # キャンバス上にイメージを配置
    on_canvas = canvas.create_image(
        0,  # x座標
        0,  # y座標
        image=ptyna_images[0],  # 配置するイメージを指定
        anchor=tk.NW,  # 配置の起点となる位置を左上隅に指定
    )

    # 応答エリアを作成
    response_area = tk.Label(
        root,  # 親要素をメインウィンドウに設定
        width=50,  # 幅を設定
        height=10,  # 高さを設定
        bg='palegreen',  # 背景色を設定
        font=font,  # フォントを設定
        relief=tk.RIDGE,  # 枠線の種類を設定
        bd=2,  # 枠線の幅を設定
        justify=tk.LEFT,
        wraplength=160
    )
    response_area.place(x=370, y=305)  # メインウィンドウ上に配置

    # フレームの作成
    frame = tk.Frame(
        root,  # 親要素はメインウィンドウ
        relief=tk.RIDGE,  # ボーダーの種類
        borderwidth=4  # ボーダー幅を設定
    )
    # 入力ボックスの作成
    entry = tk.Entry(
        frame,  # 親要素はフレーム
        width=70,  # 幅を設定
        font=font  # フォントを設定
    )
    entry.pack(side=tk.LEFT)  # フレームに左詰めで配置する
    entry.focus_set()  # 入力ボックスにフォーカスを当てる
    # ボタンの作成
    button = tk.Button(
        frame,  # 親要素はフレーム
        width=15,  # 幅を設定
        text='話す',  # ボタンに表示するテキスト
        command=talk  # クリック時にtalk()関数を呼ぶ
    )
    button.pack(side=tk.LEFT)  # フレームに左詰めで配置する
    frame.place(x=30, y=520)  # フレームを画面上に配置

    # リストボックスを作成
    lb = tk.Listbox(
        root,  # 親要素はフレーム
        width=42,  # 幅を設定
        height=30,  # 高さを設定
        font=font_log  # フォントを設定
    )
    # 縦のスクロールバーを生成
    sb1 = tk.Scrollbar(
        root,  # 親要素はフレーム
        orient=tk.VERTICAL,  # 縦方向のスクロールバーにする
        command=lb.yview  # スクロール時にListboxのyview()メソッドを呼ぶ
    )
    # 横のスクロールバーを生成
    sb2 = tk.Scrollbar(
        root,  # 親要素はフレーム
        orient=tk.HORIZONTAL,  # 横方向のスクロールバーにする
        command=lb.xview  # スクロール時にListboxのxview()メソッドを呼ぶ
    )
    # リストボックスとスクロールバーを連動させる
    lb.configure(yscrollcommand=sb1.set)
    lb.configure(xscrollcommand=sb2.set)
    # grid()でリストボックス、スクロールバーを画面上に配置
    lb.grid(row=0, column=0)
    sb1.grid(row=0, column=1, sticky=tk.NS)
    sb2.grid(row=1, column=0, sticky=tk.EW)

    # メインループ
    root.mainloop()


# =================================================
# プログラムの起点
# =================================================
if __name__ == '__main__':
    run()

