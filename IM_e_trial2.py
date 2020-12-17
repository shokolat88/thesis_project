# IM_e_demo.py for experiment with 4rules
# based on IM_e_demo.py by Shoko Ota modified by Kenji Doya
import CAclass
import numpy as np
import pandas as pd
from tkinter import *
from tkinter import ttk
import datetime
import time
import argparse

class Environment(object):
    def __init__(self, ncol, nrow, subject, state_init='zeros', seed=0):
        # ----- 変数宣言 -----
        myCAparam = CAclass.CAparam()
        self.size = myCAparam.setSize()
        #self.size       = [nrow, ncol]
        self.rule = 1
        self.rule_param = myCAparam.setParam()
        self.rules = 4
        self.ruleorder1 = np.array([])
        self.ruleplay = 'SELECT A RULE.'
        self.rng        = np.random.RandomState(seed)
        self.subject    = subject
        self.is_playing = False  # ライフゲームの再生
        self.is_ending = False  # ライフゲームの強制終了
        self.is_gamestart = False
        self.colors     = ["white", "#c24138", "#283b6c", "#469b62", "#FFD700"]   # セルの色の種類(白, ピンク, 青, 緑, 黄)
        #self.ncolors    = 3 if self.rule in [1, 2] else 4
        self.ncolors    = 2 #色の数
        self.start_time = time.time()  # 実験開始時刻の取得

        if state_init == 'zeros':
            self.state = np.zeros(self.size, dtype=int)  # temporaryステージデータ行列
        elif state_init == 'random':
            self.rng.randint(0, self.ncolors, size=self.size)

        # データ保存用変数
        #self.state_data = self.state[None]  # 記録用全ステージデータ行列
        self.state_npdata = self.state[None]
        self.state_data = pd.DataFrame([self.state.reshape(-1)], index=pd.Index([0.], name='time'))
        self.click_data = pd.DataFrame(columns=['Rule','Generation','Start','Stop','x','y'], index=pd.Index([0.], name='time'))

        self.check = np.vectorize(self._check)
        # ----- GUI -----
        # 画面初期化
        self.win = Tk()
        self.win.title("Trial2")
        self.win.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.frame1 = ttk.Frame(self.win, height=20, width=200)
        self.frame1.grid()

        #ルール番号表示
        self.ruleplay = StringVar()
        self.rulelabel = Label(self.frame1, textvariable=self.ruleplay, height=3, width=70)
        self.rulelabel.pack(anchor="nw",side="left")
        self.rulelabel.grid(row=1,column=1)
        #ゲームプレイ時間
        #self.buff = StringVar()
        #self.buff.set('100')
        #時間表示
        #self.entry  = Entry(self.frame1, textvariable = self.buff)
        #self.entry.pack()
        #self.entry.grid(row=1,column=2)

        #RULE選択ボタン設定
        self.frame2 = ttk.Frame(self.win)
        self.frame2.grid()
        self.v= IntVar()
        self.v.set(0)
        #+
        self.rulebtn = []
        for i in range(1,self.rules+1):
            self.rulebtn.append( ttk.Checkbutton(self.frame2, text="Rule%d"%i, width=10, variable=self.v, onvalue=i, command=self.change_rule))
            self.rulebtn[-1].grid(row=1,column=i)
        #/
        #self.rule1btn = ttk.Checkbutton(self.frame2, text="Rule1", variable=self.v, onvalue=1, command=self.change_rule)
        #self.rule1btn.grid(row=1,column=1)
        #self.rule2btn = ttk.Checkbutton(self.frame2, text="Rule2", variable=self.v, onvalue=2, command=self.change_rule)
        #self.rule2btn.grid(row=1,column=2)
        #self.rule3btn = ttk.Checkbutton(self.frame2, text="Rule3", variable=self.v, onvalue=3, command=self.change_rule)
        #self.rule3btn.grid(row=1,column=3)
        #self.rule4btn = ttk.Checkbutton(self.frame2, text="Rule4", variable=self.v, onvalue=4, command=self.change_rule)
        #self.rule4btn.grid(row=1,column=4)

        self.frame3 = ttk.Frame(self.win)
        self.frame3.grid()

        #- self.cw = 85
        #+
        self.cw = 680//self.size[0]  # cell size
        #/
        # キャンバスをウィンドウに載せる
        self.cv = Canvas(self.frame3, width=
        self.cw * self.size[1] + 11, height=self.cw * self.size[0] + 11)
        # self.cv = Canvas(self.win, width = CW*COLS, height = CW*ROWS)
        #self.cv.pack()
        self.cv.grid(row=1,column=1)
        self.cv.bind("<1>", lambda e: self.canvas_click(e.x, e.y))  #キャンバスがクリックされた時の関数を定義

        self.frame4 = ttk.Frame(self.win)
        self.frame4.grid()
        #ボタン表示
        self.btn = Button(self.frame4, highlightbackground="white" ,height=5, width=35, text="Start")    #ボタンの定義
        #self.btn.pack(fill='x') #ボタンの配置
        self.btn.grid(row=1,column=1)
        #self.btn.pack(anchor=NW)
        self.btn.bind('<Button-1>', self.start_click)   #ボタンがクリックされた時の関数を定義
        #次へ進むボタン
        self.nextbtn = Button(self.frame4, highlightbackground="white" ,height=5, width=35, text="End and Next")
        #self.nextbtn.pack(fill='x') #ボタンの配置
        self.nextbtn.grid(row=1,column=2)
        #self.nextbtn.pack(anchor=NW)
        self.nextbtn.bind('<Button-1>', self.end_click)   #ボタンがクリックされた時の関数を定義

    def timer(self):
        #self.time = int(self.buff.get())
        #self.buff.set('20') #１回のplay時間
        count_time = time.time() - self.gamestart_time
        if count_time < 600:
            self.win.after(1000, self.timer)
            #self.time -= 1
            #self.buff.set(str(self.time))
        else:
            selapsed = time.time() - self.start_time
            self.click_data = self.click_data.append(pd.DataFrame({'Stop': "End"}, index=pd.Index([selapsed], name='time')))
            self.on_closing()

    def change_rule(self):
        #チェックされているラジオボタンを取得
        #+
        checked = self.v.get()
        if checked > 0 and checked <= self.rules:
            self.rule = checked
        #/
        #- if checked == 1:
        #    self.rule = 1
        # elif checked == 2:
        #    self.rule = 2
        # elif checked == 3:
        #    self.rule = 3
        # elif checked == 4:
        #    self.rule = 4
        else:
            print ("Please select a rule.")
        self.ruleplay.set('RULE%d' % self.rule)
        self.rulelabel.configure(bg=self.colors[self.rule])
    #+
    def set_rule(self, _):
        # set the rule parameters
        if self.rule > 0 and self.rule <=self.rules:
            # type with [ , , ]
            inp = input("Set Rule %d [min, max, birth]: "%self.rule)
            par = np.array( [9]+eval(inp))  # 9 neighbors
            #print("Rule %d: "%self.rule, par)
            self.rule_param[self.rule-1] = par # update the table
        else:
            print ("Please select a rule.")
        self.btn["highlightbackground"] = "white"
    #/
    def start_click(self, _):
        if self.is_gamestart == False:
            self.gamestart_time = time.time()
            self.is_gamestart = not self.is_gamestart

        self.btn.configure(state=DISABLED)
        self.ruleorder1 = np.append(self.ruleorder1, self.rule)
        # ボタンONならOFFに変更し、OFFなら、ONに戻す。
        if self.btn["highlightbackground"] == self.colors[self.rule]:
            self.btn["highlightbackground"] = "white"
        else:
            self.btn["highlightbackground"] = self.colors[self.rule]

        self.is_playing = not self.is_playing
        self.is_ending = False
        selapsed = time.time() - self.start_time
        self.click_data = self.click_data.append(pd.DataFrame({'Start': "Start"}, index=pd.Index([selapsed], name='time')))

        self.timer() #タイマーカウントスタート

    def end_click(self, _):
        #StartボタンをOFF表示にする
        self.btn["highlightbackground"] = "white"
        #self.buff.set('0')
        selapsed = time.time() - self.start_time
        self.click_data = self.click_data.append(pd.DataFrame({'Stop': "Next"}, index=pd.Index([selapsed], name='time')))
        self.on_ending()

    def on_ending(self):
        self.is_playing = False
        self.is_ending = True
        self.state = np.zeros(self.size, dtype=int)
        self.draw_stage()
        self.btn["highlightbackground"] = "white"

        self.btn.configure(state=NORMAL)

    def canvas_click(self, x, y):
        xx, yy = [x // self.cw, y // self.cw]  # どのセルをクリックしたか
        elapsed = time.time() - self.start_time
        # for debugging: print ('x:{0},y:{1},time:{2}'.format(xx, yy, elapsed))
        self.click_data \
            = self.click_data.append(pd.DataFrame({'Rule': self.rule, 'Generation': self.is_playing, 'x': xx, 'y': yy}, index=pd.Index([elapsed], name='time')))
        # data[yy, xx] = not data[yy, xx] # セルの生死を反転
        self.state[yy, xx] = (self.state[yy, xx] + 1) % self.ncolors  # 色を順繰り変える
        self.draw_stage()

    def on_closing(self):
        current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M')  # 実験日の取得

        self.click_data.to_csv('{0}_sub_{1}_trial2_click.csv'.format(current_time, self.subject))  # クリック情報
        np.save('{0}_sub_{1}_trial2_env.npy'.format(current_time, self.subject), self.state_npdata)  # 状態遷移
        self.state_data.to_csv('{0}_sub_{1}_trial2_state.csv'.format(current_time, self.subject))  # 状態遷移

        self.win.destroy()

    def game_loop(self): # 指定時間ミリ秒ごとに世代を進める

        if self.is_playing:
            self.next_turn()  # 世代を進める
            self.draw_stage()  # ステージを描画

        self.win.after(1500, self.game_loop)  # 指定時間後に再度描画

    def draw_stage(self):
        # ステージを描画
        self.cv.delete('all')
        for y in range(self.size[0]):
            for x in range(self.size[1]):
                # data[y][x]> : continue
                x1, y1 = [x * self.cw + 8, y * self.cw + 8]
                self.cv.create_rectangle(x1, y1, x1 + self.cw, y1 + self.cw)
                if self.state[y,x] != 0:
                    self.cv.create_rectangle(x1, y1, x1 + self.cw, y1 + self.cw,
                                         fill=self.colors[self.rule])

    def next_turn(self):
        # データを次の世代に進める
        seselapsed = time.time() - self.start_time
        self.state_npdata = np.vstack([self.state_npdata, self.state[None]])
        self.state = self.state.reshape(-1)
        self.state_data \
            = self.state_data.append(pd.DataFrame([self.state], index=pd.Index([seselapsed], name='time')))
        self.state = self.state.reshape(8, 8)
        self.state      = self.check(np.arange(self.size[1]).reshape(1, -1), np.arange(self.size[0]).reshape(-1, 1))

    def _check(self, x, y):
        # ルールに沿って次世代のcolorを決める
        if self.rule > 0 and self.rule <= self.rules:
            neighbor = self.rule_param[self.rule-1,0]
            c_survive_min = self.rule_param[self.rule-1,1]
            c_survive_max = self.rule_param[self.rule-1,2]
            c_birth       = self.rule_param[self.rule-1,3]
        #if self.rule == 1:
            # ルールの設定
        #    neighbor = 9
        #    c_survive_min = 3  # 生存の条件数minimum
        #    c_survive_max = 5  # 生存の条件数maximum
        #    c_birth       = 1  # 誕生の条件数

        #elif self.rule == 2:
            # ルールの設定
        #    neighbor = 9
        #    c_survive_max = 5  # 生存の条件数maximum
        #    c_birth       = 2  # 誕生の条件数

        #elif self.rule == 3:
            # ルールの設定
        #    neighbor = 9
        #    c_survive_min = 3  # 生存の条件数minimum
        #    c_survive_max = 3 # 生存の条件数maximum
        #    c_birth       = 1  # 誕生の条件数

        #elif self.rule == 4:
            # ルールの設定
        #    neighbor = 9
        #    c_survive_min = 3  # 生存の条件数minimum
        #    c_survive_max = 3  # 生存の条件数maximum
        #    c_birth       = 1  # 誕生の条件数
        else:
            raise(ValueError('Rule {} is not defined.'.format(self.rule)))

        # 真ん中のセルのcolorを調べる
        centercolor = self.state[y, x]
        # 周囲のセルのcolorを調べる
        cnt = np.zeros(self.ncolors)
        nei_5 = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        nei_5b = [(-1, -1), (1, 1), (-1, 1), (1, -1)]
        nei_9 = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]

        if neighbor == 5:
            tbl = nei_5
        if neighbor == 6:
            tbl = nei_5b
        elif neighbor == 9:
            tbl = nei_9
        else:
            raise(ValueError('Nighbor {} is not defined.'.format(self.rule)))

        for t in tbl:
            xx, yy = [x + t[0], y + t[1]]
            xx = (xx + self.size[1]) % self.size[1]
            yy = (yy + self.size[0]) % self.size[0]
            if 0 <= xx < self.size[1] and 0 <= yy < self.size[0]:
                color = self.state[yy, xx]  # colorのどの色かを特定
                cnt[color] += 1  # 該当の色の数をcntに追加
            #colornum = cnt.max()  # 一番多い色の数は？（同数の場合は、colorの配列順に優勢)
            #index    = cnt.argmax()  # 一番多い色のindex番号は？
            #print(cnt[centercolor])
        #CA
        if centercolor != 0:
            if cnt[centercolor] >= c_survive_min and cnt[centercolor] <= c_survive_max:
                    return centercolor % self.ncolors # 生存のルール
            else: return 0 # 死のルール
        else:
            for i,x in  enumerate(cnt):
                if cnt[i] == c_birth: # 誕生のルール
                    if i != 0:
                        return i % self.ncolors
            else: return 0 # 死のルール


def main(size, subject, seed):
    env = Environment(ncol=size, nrow=size, subject=subject, state_init='zeros', seed=seed)
    env.draw_stage()
    env.game_loop()  # ゲームループを実行
    env.win.mainloop()  # イベントループ

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #parser.add_argument('--rule', dest='rule', type=int, help='Rule No.', required=True)
    parser.add_argument('--subject', dest='subject', type=int, help='Subject No.', required=True)
    parser.add_argument('--size', dest='size', type=int, help='Grid size', default=8)
    parser.add_argument('--seed', dest='seed', help='Seed for numpy random number generator', default=None)

    condition = parser.parse_args()

    main(condition.size, condition.subject, condition.seed)
