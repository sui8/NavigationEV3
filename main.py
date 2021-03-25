#インポート群
import wx #GUI
import tkinter as tk #TKinter無効化用
from tkinter import messagebox as msgbox #メッセージボックス
from PIL import Image #画像取り扱い
import os #Windows環境用
import sys #システム終了用
from ctypes import windll #Windows環境画面解像度用
import configparser #Config用
import zipfile #NCPファイル用
import configparser #Config(ini)読み込み用

#変数定義群
TitleName = "NavigationEV3 ReWrite" #タイトル名
Version = "3.0.0" #バージョン

DisplayMax = [1920, 1080]
DisplayMin = [1280, 720]
DefaultWindowSize = 0.8
SubWindowSize = [350, 400]

FontSize = 10
ConfigPath = "Config/Config.ini"

DebugOutput = True #デバッグ情報を出力するか
#-------------------------------------------------

#リストの定義
DisplaySize = []
WindowSize = []

#定数定義
ConfigLoader = configparser.ConfigParser()

#デバッグ用関数
def Debug(text):
    if DebugOutput == True:
        print(text)

#---起動------------------------------------------

#Tkinterのroot無効化
tk.Tk().withdraw()

#Windowsにおいての画面横幅と縦幅取得
DisplaySize.append(int(windll.user32.GetSystemMetrics(0)))
DisplaySize.append(int(windll.user32.GetSystemMetrics(1)))
Debug("DisplaySize " + str(DisplaySize))

#最低要件確認
if not DisplaySize[0] >= DisplayMin[0] or not DisplaySize[1] >= DisplayMin[1]:
    msgbox.showerror(TitleName, "このPCはシステム最低要件を満たしていないため、起動できません。")
    sys.exit(0)

#Config読み込み（try exceptで対策必要）
ConfigLoader.read(ConfigPath, encoding="utf-8")
Config = ConfigLoader["Settings"]

DefaultWindowSize = float(format(float(Config.get("Zoom")), ".2f"))

#ウィンドウサイズ設定
WindowSize.append(int(format(round(DisplaySize[0] * DefaultWindowSize, 0), ".0f")))
WindowSize.append(int(format(round(DisplaySize[1] * DefaultWindowSize, 0), ".0f")))
Debug("WindowSize " + str(WindowSize))

#メインウィンドウ起動
app = wx.App()
frame = wx.Frame(None, -1, str(TitleName) + " Ver" + str(Version), size=(WindowSize[0],WindowSize[1]))
frame.Show()


#ボタン描画
wx.Button(frame, wx.ID_OPEN, pos=(10,10), label="開く")
wx.Button(frame, wx.ID_CLOSE, pos=(10,40))
wx.Button(frame, wx.ID_NEW, pos=(100,10))
wx.Button(frame, wx.ID_SAVE, pos=(100,40))
wx.Button(frame, wx.ID_HELP, pos=(200,40))



#アプリ実行
app.MainLoop()
