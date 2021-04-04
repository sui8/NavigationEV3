#インポート群
import wx #GUI
#import tkinter as tk #TKinter無効化用
#from tkinter import messagebox as msgbox #メッセージボックス
from PIL import Image , ImageTk #画像取り扱い
import os #Windows環境用
import sys #システム終了用
from ctypes import windll #Windows環境画面解像度用
import configparser #Config用
import zipfile #NCPファイル用
import configparser #Config(ini)読み込み用


#変数定義群
TitleName = "NavigationEV3 ReWrite" #タイトル名
Version = "3.0.0α-Dev5" #バージョン
Developer = "© 2020-2021 Kenta Sui"

DisplayMax = [1920, 1080]
DisplayMin = [1280, 720]
WindowRatio = [16, 9]
SubWindowSize = [350, 400]

FontSize = 10
ConfigPath = "Config/Config.ini"

DebugOutput = True #デバッグ情報を出力するか

CourtImagePath = "Data/Default.png"

#----定義・初期設定等---------------------------------------

#リストの定義
DisplaySize = []
WindowSize = []

#定数定義
ConfigLoader = configparser.ConfigParser()
WindowRatio = WindowRatio[0] / WindowRatio[1]

#デバッグ用関数
def Debug(text):
    if DebugOutput == True:
        print(text)

#---起動------------------------------------------

#初期設定出力（※将来的にConfigに移行。）
Debug("--Debug Log--")
Debug("{0} Ver{1}".format(TitleName, Version))
Debug(Developer)
Debug("\n--Constants--")
Debug("DisplayMax: {0}".format(DisplayMax))
Debug("DisplayMin: {0}".format(DisplayMin))
Debug("WindowRatio(Calculated): {0}".format(WindowRatio))
Debug("FontSize: {0}".format(FontSize))
Debug("ConfigPath: {0}".format(ConfigPath))
Debug("CourtImagePath: {0}".format(CourtImagePath))

#Windowsにおいての画面横幅と縦幅取得
DisplaySize.append(int(windll.user32.GetSystemMetrics(0)))
DisplaySize.append(int(windll.user32.GetSystemMetrics(1)))
Debug("DisplaySize {0}".format(DisplaySize))

#最低要件確認
if not DisplaySize[0] >= DisplayMin[0] or not DisplaySize[1] >= DisplayMin[1]:
    wx.MessageDialog(None, "このPCはシステム最低要件を満たしていないため、起動できません。", TitleName, style=wx.ICON_ERROR).ShowModal()
    sys.exit(0)

#Config読み込み（try exceptで対策必要）
ConfigLoader.read(ConfigPath, encoding="utf-8")
Config = ConfigLoader["Settings"]
Debug("\n> The configuration file has been successfully loaded.")
Debug("\n--User defined constants(Config)--")

WindowSizeScale = float(format(float(Config.get("Zoom")), ".2f")) #ウィンドウ表示倍率
Debug("WindowSizeScale: {0}".format(WindowSizeScale))

#画面比率計算と補正後ウィンドウサイズ算出（16:9）
if DisplaySize[0] / DisplaySize[1] == WindowRatio: #画面比率が16:9の時（何もせず代入）
    WindowSizeX = (DisplaySize[0])
    WindowSizeY = (DisplaySize[1])
    
elif DisplaySize[0] / DisplaySize[1] > WindowRatio: #画面比率が16:9より大きい時
    WindowSizeY = DisplaySize[1]
    WindowSizeX = WindowSizeY * WindowRatio #縦側に空きを作る

else: #画面比率が16:9より小さい時
    WindowSizeX = DisplaySize[0]
    WindowSizeY = WindowSizeX / WindowRatio
    
#ウィンドウサイズ設定（ConfigのZoom値を掛ける）
WindowSizeX = (int(format(round(WindowSizeX * WindowSizeScale, 0), ".0f")))
WindowSizeY = (int(format(round(WindowSizeY * WindowSizeScale, 0), ".0f")))
Debug("WindowSize [{0}, {1}]".format(WindowSizeX, WindowSizeY))

#メインウィンドウ起動
app = wx.App()
frame = wx.Frame(None, -1, "{0} Ver {1}".format(TitleName, Version), size=(WindowSizeX,WindowSizeY))
frame.Show()

#---関数------------------------------------------

#退出用
def Exit(event):
    sys.exit(0)

#ファイルオープン
def AskFileOpen(event):
    global TitleName
    FileTypes = "NavigationEV3 ReWrite ファイル (*.nrf) |*.nrf|" "すべてのファイル (*.*) |*.*"
    OpenFileDialog = wx.FileDialog(frame, message="開く", wildcard=FileTypes, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

    #ユーザーがキャンセルした場合、スルー
    if OpenFileDialog.ShowModal() != wx.ID_OK:
        return

    OpenFilePath = OpenFileDialog.GetPath()
    wx.MessageDialog(None, "あなたの選択した読み込みファイル\n{0}\n※読み込み昨日は未実装です".format(OpenFilePath), TitleName).ShowModal()
    OpenFileDialog.Destroy()

#新規ファイルオープン
def NewFileCreate(event):
    global TitleName
    wx.MessageDialog(None, "未実装です", TitleName).ShowModal()

#ファイル上書き
def FileOverWrite(event):
    global TitleName
    wx.MessageDialog(None, "未実装です", TitleName).ShowModal()

#ファイルの名前を付けて保存
def NewFileSave(event):
    global TitleName
    FileTypes = "NavigationEV3 ReWrite ファイル (*.nrf) |*.nrf|" "すべてのファイル (*.*) |*.*"
    SaveFileDialog = wx.FileDialog(frame, message="名前を付けて保存", wildcard=FileTypes, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

    #ユーザーがキャンセルした場合、スルー
    if SaveFileDialog.ShowModal() != wx.ID_OK:
        return

    SaveFilePath = SaveFileDialog.GetPath()
    wx.MessageDialog(None, "あなたの選択した保存先\n{0}\n※保存機能は未実装です".format(SaveFilePath), TitleName).ShowModal()
    SaveFileDialog.Destroy()

#このソフトウェアについて
def About(event):
    global TitleName
    wx.MessageDialog(None, "未実装です", TitleName).ShowModal()

#----ボタン類描画---------------------------------------

#ボタン描画（一時無効）
'''
Button_Open = wx.Button(frame, wx.ID_OPEN, pos=(10,10), label="開く")
Button_Close = wx.Button(frame, wx.ID_CLOSE, pos=(10,40))
Button_New = wx.Button(frame, wx.ID_NEW, pos=(100,10))
Button_Save = wx.Button(frame, wx.ID_SAVE, pos=(100,40))
Button_Help = wx.Button(frame, wx.ID_HELP, pos=(200,40))

Button_Open.Bind(wx.EVT_BUTTON, AskFileOpen)
Button_Close.Bind(wx.EVT_BUTTON, Exit)
Button_New.Bind(wx.EVT_BUTTON, NewFileCreate)
Button_Save.Bind(wx.EVT_BUTTON, FileOverWrite)
'''

#ツールバー描画
Menubar = wx.MenuBar()
FileMenu = wx.Menu()
FileMenu.Append(1, '新規(&N)', '新規のプログラムを作成する')
FileMenu.Append(2, '開く(&O)', '作成したプログラムを開く')
FileMenu.Append(3, '保存(&S)', '作成したプログラムを上書き保存する')
FileMenu.Append(4, '名前を付けて保存(&A)', '作成したプログラムを名前を付けて保存する')
FileMenu.AppendSeparator()
#FileMenu.AppendItem(wx.MenuItem(FileMenu, ID_EXIT, '終了(&E)\tCtrl+E', 'ソフトウェアを終了'))
FileMenu.Append(5, '終了(&E)', 'ソフトウェアを終了する')

frame.Bind(wx.EVT_MENU, NewFileCreate, id=1)
frame.Bind(wx.EVT_MENU, AskFileOpen, id=2)
frame.Bind(wx.EVT_MENU, FileOverWrite, id=3)
frame.Bind(wx.EVT_MENU, NewFileSave, id=4)
frame.Bind(wx.EVT_MENU, Exit, id=5)
Menubar.Append(FileMenu, 'ファイル(&F)')
frame.SetMenuBar(Menubar)

FileMenu2 = wx.Menu()
FileMenu2.Append(6, '一つ戻す(&Z)', 'プログラムを一つ戻す')
FileMenu2.Append(7, '全て削除(&U)', 'プログラムを白紙に戻す')
Menubar.Append(FileMenu2, '編集(&E)')
frame.SetMenuBar(Menubar)

FileMenu3 = wx.Menu()
FileMenu3.Append(8, 'マニュアル(&H)', 'このソフトウェアのマニュアルを表示')
FileMenu3.Append(9, 'アップデートのチェック(&U)', 'ソフトウェアのアップデートを確認')

FileMenu3.AppendSeparator()

FileMenu3.Append(10, 'このソフトウェアについて(&A)', 'このソフトウェアの情報を表示します')
Menubar.Append(FileMenu3, 'ヘルプ(&H)')

frame.Bind(wx.EVT_MENU, About, id=10)

frame.SetMenuBar(Menubar)

#---コート画像描画-----------------------------------------

#コート画像読み込みと貼り付け
CourtImage = wx.Image(CourtImagePath)
CI_Bitmap = CourtImage.ConvertToBitmap()
wx.StaticBitmap(frame, -1, CI_Bitmap, pos=(0, 0), size=CourtImage.GetSize())

#アプリ実行
app.MainLoop()
