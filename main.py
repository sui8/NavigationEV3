#インポート群
import wx #GUI
#from PIL import Image #画像取り扱い
import os #Windows環境用
import sys #システム終了用
from ctypes import windll #Windows環境画面解像度用
import configparser #Config用
import zipfile #NCPファイル用
import configparser #Config(ini)読み込み用
import subprocess #ファイルオープン用
import webbrowser #ウェブブラウザーオープン用
import math #計算用
import json #JSONファイル管理
import csv #.nrpファイル（csv）用


#変数定義群
TitleName = "NavigationEV3 ReWrite" #タイトル名
Version = "3.0.0α-Dev13a" #バージョン
Developer = "© 2020-2023 Kenta Sui"

DisplayMax = [1920, 1080]
DisplayMin = [1280, 720]
WindowRatio = [16, 9]
AboutWindowSize = [550, 480]
ControlWindowSize = [350, 500]

FontSize = 10
ConfigPath = "Config/Config.ini"

DebugOutput = True #デバッグ情報を出力するか

DefaultRobotImagePath = "Data/Robot.png"

PackagePath = "Packages" #パッケージが入るフォルダ指定
DefaultPackage = "Data/Default" #デフォルトパッケージパスと名前を指定
DefaultPackageCI = "Court.png" #パッケージ内のCourtImageの名前指定
DefaultPackageInfo = "Config.ini" #パッケージ内のPackageInfoの名前指定

UserGuideURL = "https://example.com"
UserGuidePath = "Data/UserGuide.txt" #オフラインユーザーガイドのパス指定

'''----定義・初期設定等---------------------------------------'''

#変数・リストの定義
DisplaySize = []
WindowSize = []
CI_Ratio = []
PrevPos = []
NewPos= []
RobotCounter = 0
RobotMillageDatas = []
RI_Correct = []
RobotImages = []

#定数定義
ConfigLoader = configparser.ConfigParser()
WindowRatio = WindowRatio[0] / WindowRatio[1]

#デバッグ用関数
def Debug(text):
    if DebugOutput == True:
        print(text)

#ビットマップリスケール関数
def ReScaleBitmap (Bitmap, Width, Height):
    #画像のリサイズをして戻り値
    Image = wx.ImageFromBitmap(Bitmap)
    Image = Image.Scale(Width, Height, wx.IMAGE_QUALITY_HIGH)
    Result = wx.BitmapFromImage(Image)
    return Result
    

'''---起動------------------------------------------'''

#初期設定出力（※将来的にConfigに移行。）
Debug("--Debug Log--")
Debug("{0} Ver{1}".format(TitleName, Version))
Debug(Developer)
Debug("\n--Constants--")
Debug("DisplayMax: {0}".format(DisplayMax))
Debug("DisplayMin: {0}".format(DisplayMin))
Debug("WindowRatio(Calculated): {0}".format(WindowRatio))
Debug("AboutWindowSize: {0}".format(AboutWindowSize))
Debug("ControlWindowSize: {0}".format(ControlWindowSize))
Debug("FontSize: {0}".format(FontSize))
Debug("ConfigPath: {0}".format(ConfigPath))

#Windowsにおいての画面横幅と縦幅取得
DisplaySize.append(int(windll.user32.GetSystemMetrics(0)))
DisplaySize.append(int(windll.user32.GetSystemMetrics(1)))
Debug("DisplaySize: {0}".format(DisplaySize))

#最低要件確認
if not DisplaySize[0] >= DisplayMin[0] or not DisplaySize[1] >= DisplayMin[1]:
    wx.MessageDialog(None, "このPCはシステム最低要件を満たしていないため、起動できません。", TitleName, style=wx.ICON_ERROR).ShowModal()
    sys.exit(0)

#Config読み込み（try exceptで対策必要・開発中）
ConfigLoader.read(ConfigPath, encoding="utf-8")

try:
    Config = ConfigLoader["Settings"]
except Expection as E:
    Debug("[Error] The setting section was not found. Use default settings.")
else:

    try:
        WindowSizeScale = float(format(float(Config.get("Zoom")), ".2f")) #ウィンドウ表示倍率
    except Expection as E:
        Debug("[Error] 'Zoom' setting was not found. Use default settings.")
    else:
        Debug("\n> The configuration file has been successfully loaded.")
        Debug("\n--User defined constants(Config)--")

        RobotImagePath = str(Config.get("RobotImagePath")) #ロボット画像パス
        Package = str(Config.get("Package")) #コートパック指定
        DecimalDigit = int(Config.get("DecimalDigit")) #ロボット距離小数点以下桁数指定
        TireRotationDecimalDigit = int(Config.get("TireRotationDecimalDigit")) #ロボット距離（タイヤ回転数）小数点以下桁数指定
        TireCircumference = float(Config.get("TireCircumference")) #タイヤ円周
        
        Debug("WindowSizeScale: {0}".format(WindowSizeScale))
        Debug("RobotImagePath: {0}".format(RobotImagePath))
        Debug("Package: {0}".format(Package))
        Debug("DecimalDegit: {0}".format(DecimalDigit))
        Debug("TireRotationDecimalDegit: {0}".format(TireRotationDecimalDigit))
        Debug("TireCircumference: {0}".format(TireCircumference))


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

#デフォルト最大解像度からの倍率（16:9と仮定して）
DisplayMagnification = DisplayMax[0] / DisplaySize[0]
Debug("DisplayMagnification: {0}".format(DisplayMagnification))
    
#ウィンドウサイズ設定（ConfigのZoom値を掛ける）
WindowSizeX = (int(format(round(WindowSizeX * WindowSizeScale, 0), ".0f")))
WindowSizeY = (int(format(round(WindowSizeY * WindowSizeScale, 0), ".0f")))
Debug("WindowSize: [{0}, {1}]".format(WindowSizeX, WindowSizeY))



#指定されたパッケージが存在するか
if not os.path.isfile("{0}/{1}.ncp".format(PackagePath, Package)):
    Package = "Default"
    Debug("[Error] Could not find the package. Use the default package.")

# zipファイルに含まれているテキストファイルの読み込み（エラー対策済）
try:
    with zipfile.ZipFile("{0}/{1}.ncp".format(PackagePath, Package)) as ncp:
        with ncp.open(DefaultPackageInfo) as ncp_info:
            ConfigLoader.read(ncp_info, encoding="utf-8")
            Config = ConfigLoader["Settings"]
            PackageName = str(Config.get("PackageName"))

except Exception as e:
    Debug("[Error] Could not load PackageInfo in the package. Use the default package.")
    Debug(e)

    try:
        with zipfile.ZipFile("{0}.ncp".format(DefaultPackage)) as ncp:
            with ncp.open(DefaultPackageInfo) as ncp_info:
                ConfigLoader.read(ncp_info, encoding="utf-8")
                Config = ConfigLoader["Settings"]
                PackageName = str(Config.get("PackageName"))

    except Exception as e:
        app = wx.App()
        wx.MessageDialog(None, "回復不能なエラーが発生しました。ソフトウェアを再インストールしてください。\n[Error: PackageInfo in the 'Default' package is missing or corrupt.]", TitleName, style=wx.ICON_ERROR).ShowModal()
        Debug("[Error] Default package is damaged.")
        Debug(e)
        sys.exit()

# zipファイルに含まれているコートファイルの読み込み（エラー対策済）
try:
    with zipfile.ZipFile("{0}/{1}.ncp".format(PackagePath, Package)) as ncp:
        ncp.extract(member=DefaultPackageCI, path="{0}/".format(PackagePath))
        CourtImagePath = "{0}/{1}".format(PackagePath, DefaultPackageCI)

except Exception as e:
    Debug("[Error] Could not load CourtImage in the package. Use the default package.")
    Debug(e)

    try:
        with zipfile.ZipFile("{0}.ncp".format(DefaultPackage)) as ncp:
            ncp.extract(member=DefaultPackageCI, path="{0}/".format(PackagePath))
            CourtImagePath = "{0}/{1}".format(PackagePath, DefaultPackageCI)

    except Exception as e:
        app = wx.App()
        wx.MessageDialog(None, "回復不能なエラーが発生しました。ソフトウェアを再インストールしてください。\n[Error: PackageInfo in the 'Default' package is missing or corrupt.]", TitleName, style=wx.ICON_ERROR).ShowModal()
        Debug("[Error] Default package is damaged.")
        Debug(e)
        sys.exit()


#Debug("HomeDirectory: {0}".format(HomeDirectory))


'''---ウィンドウ別クラス（メイン）----------------------------------------'''

#ソフトウェアについてタブ
class AboutWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(AboutWindowSize), style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        Panel = wx.Panel(self, wx.ID_ANY)

        #テキスト描画準備
        text_1 = wx.StaticText(Panel, wx.ID_ANY, "", style=wx.TE_CENTER)
        text_2 = wx.StaticText(Panel, wx.ID_ANY, TitleName, style=wx.TE_CENTER)
        text_3 = wx.StaticText(Panel, wx.ID_ANY, "", style=wx.TE_CENTER)

        #フォント設定
        FontSetting = wx.Font(32, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        Font_NewLine = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        #ボタン描画
        '''Button_OK = wx.Button(self, 0000, pos=(440,410), label="OK", size=(85,22))
        self.Bind(wx.EVT_BUTTON, print("hogehogefugafugapiyopiyo"), Button_OK)
        '''
        layout = wx.BoxSizer(wx.VERTICAL)
        #layout = wx.GridSizer(rows=2, cols=2, gap=(0, 0))
        text_1.SetFont(Font_NewLine)
        text_2.SetFont(FontSetting)
        text_3.SetFont(Font_NewLine)
        layout.Add(text_1, flag=wx.GROW)
        layout.Add(text_2, flag=wx.GROW)
        layout.Add(text_3, flag=wx.GROW)
        layout.Add(wx.StaticLine(Panel), flag=wx.GROW)
        #layout.Add(Button_OK, 0, wx.GROW)
        
        Panel.SetSizer(layout)
        
        self.Show()


#同時起動タブ（コンパネ）
#複数起動してしまうのでActivateEvent使うと良いかも
class ControlWindow(wx.Frame):
    #Entry操作系
    def EntryClear(self, parent):
        C_TextEntry1.Clear()

    def EntryCopy(self, parent):
        EntryValue = C_TextEntry1.GetValue()
        wx.TheClipboard.SetData(wx.TextDataObject(EntryValue))
        Debug("> Entry value has been Copied.")

    #ウィンドウ
    def __init__(self, parent, title):
        global C_TextEntry1

        if self.FindWindowByName(title) is None:
            wx.Frame.__init__(self, parent, title=title, size=(ControlWindowSize), style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

            Panel = wx.Panel(self, wx.ID_ANY)

            C_Text1 = wx.StaticText(Panel, -1, "○ロボット走行距離ログ", (5, 10))
            C_Text2 = wx.StaticText(Panel, -1, "○機能パネル", (5, 260))
            C_TextEntry1 = wx.TextCtrl(Panel, wx.ID_ANY, style=wx.TE_MULTILINE, size=(325, 220), pos=(5, 30))
            
            LogCopy_Button = wx.Button(Panel, label="データコピー", pos=(205, 5), size=(60, 25))
            #削除候補
            LogDelete_Button = wx.Button(Panel, label="履歴削除", pos=(270, 5), size=(60, 25))

            #ButtonにBind
            LogCopy_Button.Bind(wx.EVT_BUTTON, self.EntryCopy)
            LogDelete_Button.Bind(wx.EVT_BUTTON, self.EntryClear)
            
            self.Show()


#メインウィンドウ
class MainWindow(wx.Frame):
        
    #---関数------------------------------------------

    #退出用
    def Exit(self, event):
        sys.exit(0)

    #ファイルオープン
    def AskFileOpen(self, event):
        FileTypes = "NavigationEV3 ReWrite ファイル (*.nrp) |*.nrp|" "すべてのファイル (*.*) |*.*"
        OpenFileDialog = wx.FileDialog(self, message="開く", wildcard=FileTypes, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        #ユーザーがキャンセルした場合、スルー
        if OpenFileDialog.ShowModal() != wx.ID_OK:
            return

        OpenFilePath = OpenFileDialog.GetPath()
        wx.MessageDialog(None, "あなたの選択した読み込みファイル\n{0}\n※読み込み機能は未実装です".format(OpenFilePath), TitleName).ShowModal()
        OpenFileDialog.Destroy()

    #新規ファイル作成
    def NewFileCreate(self, event):
        global RobotImages
        if RobotImages:
            Result = wx.MessageDialog(None, "現在の変更内容を破棄しますか？", TitleName, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION).ShowModal()

            if Result == wx.ID_YES:
                RobotCounter = 0
                RobotMillageDatas = []
                ControlWindow.EntryClear("","")
                    
                for i in RobotImages:
                    i.Destroy()

                RobotImages = []

    #ファイル上書き
    def FileOverWrite(self, event):
        wx.MessageDialog(None, "未実装です", TitleName).ShowModal()

    #ファイルの名前を付けて保存
    def NewFileSave(self, event):
        global RobotMillageDatas
        FileTypes = "NavigationEV3 ReWrite ファイル (*.nrp) |*.nrp|" "すべてのファイル (*.*) |*.*"
        SaveFileDialog = wx.FileDialog(self, message="名前を付けて保存", wildcard=FileTypes, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        #ユーザーがキャンセルした場合、スルー
        if SaveFileDialog.ShowModal() != wx.ID_OK:
            return

        SaveFilePath = SaveFileDialog.GetPath()

        #.nrpとして保存
        with open(SaveFilePath, "w", encoding="UTF-8") as f:
            NRPWriter = csv.writer(f, lineterminator="\n") #writerオブジェクトの作成（改行記号で行を区切る）
            NRPWriter.writerows(RobotMillageDatas) #csvファイルに書き込み
            
        wx.MessageDialog(None, "プログラムファイルを\n{0}\nに保存しました。".format(SaveFilePath), TitleName).ShowModal()
        SaveFileDialog.Destroy()

    #1つ戻る
    def UndoRobot(self, event):
        wx.MessageDialog(None, "未実装です", TitleName).ShowModal()
    
    #全削除
    def AllRobotsClear(self, event):
        global RobotCounter, RobotMillageDatas, RobotImages
        Result = wx.MessageDialog(None, "全てのロボット位置情報を削除しますか？", TitleName, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION).ShowModal()

        if Result == wx.ID_YES:
            RobotCounter = 0
            RobotMillageDatas = []
            ControlWindow.EntryClear("","")
                
            for i in RobotImages:
                i.Destroy()

            RobotImages = []


    #オンラインマニュアル
    def OnlineUserGuide(self, event):
        webbrowser.open(UserGuideURL)

    #オフラインマニュアル
    '''def OfflineUserGuide(self, event):
        subprocess.Popen(cwd=UserGuidePath)'''

    #このソフトウェアについて
    def About(self, event):
        AboutWindow(self, TitleName)
        app.SetTopWindow(self)

    #コントロールパネルウィンドウ
    def ControlPanel(self, event):
        ControlWindow(self, TitleName + " ControlPanel")
        app.SetTopWindow(self)

    #プログラミング言語での読み込み
    def LoadLib(self, language):
        global LibConfig, LibFiles
        Debug("--LoadLib: {0} --".format(language))
        
        #LoadLib 各種変数
        #・LibConfig...Config.json
        #・LibFiles...Config.json内のfilesの中身
        
        if os.path.exists("Lib/{0}/Config.json".format(language)) != True:
            Debug("[Error] LoadLib could not find the '{0}' library.".format(language))
            Debug("-----------------")
            Status = False
            return Status
            
        else:
            Debug("> LoadLib has successfully discovered the '{0}' library.".format(language))

            #Config.jsonの読み込み
            try:
                with open("Lib/{0}/Config.json".format(language), 'r') as LibConfig:
                    LibConfig = json.load(LibConfig)
            except:
                Debug("[Error] LoadLib could not read the Config.json of the '{0}' library.".format(language))
                Debug("-----------------")
                Status = False
                return Status
            else:
                Debug("> LoadLib has successfully loaded Config.json of the '{0}' library.".format(language))

                #Config.jsonの要素のチェック（エラーが起こった場合は"Unknown"と置く）
                LibConfigElements = ["name", "version", "author", "language", "files"]

                for i in LibConfigElements:
                    try:
                        LibConfigCheck = str(LibConfig[i])
                    except:
                        Debug("[Error] LoadLib could not load element '{1}' of Config.json of '{0}' library.".format(language, i))
                        Debug("-----------------")
                        LibConfig[i] = "Unknown"
                        Debug("> {0}: {1}".format(i, LibConfig[i]))
                    else:
                        Debug("> {0}: {1}".format(i, LibConfig[i]))
                

                ##各種ライブラリファイル読み込み
                LibFiles = {}

                for i in range(len(LibConfig['files'])):
                    LibFiles[str(LibConfig['files'][i])] = ""


                for i in LibFiles.keys():

                    #ファイルの有無を確認
                    if os.path.exists("Lib/{0}/{1}".format(language, i)) != True:
                        Debug("[Error] LoadLib could not find the file '{0}'.".format(i))
                        Debug("-----------------")
                        LoadStatus = False
                        return LoadStatus
                    else:
                        #ファイル破損（内容があるか）確認
                        try:
                            with open("Lib/{0}/{1}".format(language, i), 'r', encoding='UTF-8') as f:
                                LibFiles['{0}'.format(i)] = f.read()
                        except:
                            Debug("[Error] LoadLib could not load the file '{0}'.".format(i))
                            Debug("-----------------")
                            LoadStatus = False
                            return LoadStatus
                        else:
                            Debug("> LoadLib has loaded the file '{0}'.".format(i))


                Debug("> LoadLib has successfully loaded all files.")
                Debug("-----------------")
                                                
                LoadStatus = True
                return LoadStatus

    #EV3devソースコードに変換
    def ConvertToev3dev(self, event):
        #プログラムない場合はスルー
        if len(RobotMillageDatas) == 0:
            wx.MessageDialog(None, "プログラムを作成してから実行してください", TitleName, style=wx.ICON_ERROR).ShowModal()
            return
        
        #ファイル保存
        FileTypes = "ev3dev プログラムファイル (*.py) |*.py|" "テキスト ドキュメント (*.txt) |*.txt|" "すべてのファイル (*.*) |*.*"
        SaveFileDialog = wx.FileDialog(self, message="名前を付けて保存", wildcard=FileTypes, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        #ユーザーがキャンセルした場合、スルー
        if SaveFileDialog.ShowModal() != wx.ID_OK:
            return

        SaveFilePath = SaveFileDialog.GetPath()
        SaveFileDialog.Destroy()
        
        #LoadLibでライブラリ読み込み
        LoadStatus = self.LoadLib("ev3dev")

        #正しくロード出来たかステータスチェック
        if LoadStatus != True:
            Debug("[Error] Could not load ev3dev library.")
            wx.MessageDialog(None, "'ev3dev' ライブラリが破損しているため、プログラムの変換に失敗しました。", TitleName, style=wx.ICON_ERROR).ShowModal()
            return
        
        else:
            #プログラム書き込みスタート
            RobotMillages = []
            for i in range(len(RobotMillageDatas) - 1):
                i += 1
                RobotMillages.append(RobotMillageDatas[i][4])

            ev3dev_Program = LibFiles['InitialSettings.ini'] + "\n" #初期設定
            
            ev3dev_Program += "\n"

            ev3dev_Program += LibFiles['MotorSet.ini'].format("B", "Large") + "\n" #モーター設定
            ev3dev_Program += LibFiles['MotorSet.ini'].format("C", "Large") + "\n" #モーター設定

            ev3dev_Program += "\n"

            #RobotMillagesに基づいて走るプログラム追加
            for i in RobotMillages:
                ev3dev_Program += LibFiles['MotorRun.ini'].format("B", i, 500, "brake") + "\n"
                ev3dev_Program += LibFiles['MotorRun.ini'].format("C", i, 500, "brake") + "\n"

                ev3dev_Program += "\n"

            print(ev3dev_Program)

            try:
                with open(SaveFilePath, mode='w') as f:
                    f.write(ev3dev_Program)
            except:
                wx.MessageDialog(None, "ファイルの保存に失敗しました。\n保存場所を確認してください。", TitleName, style=wx.ICON_ERROR).ShowModal()
            else:
                wx.MessageDialog(None, "プログラムの変換に成功しました", TitleName).ShowModal()
                

    #EV3RTソースコードに変換
    def ConvertToEV3RT(self, event):
        wx.MessageDialog(None, "未実装です", TitleName).ShowModal()


    #アップデートの確認
    def CheckUpdate(self, event):
        wx.MessageDialog(None, "未実装です", TitleName).ShowModal()


    ##ロボット画像処理関係

    #ロボット走行距離算出
    def MileageCal(self, PrevPos, NewPos):
        global RobotCounter, RobotMillageDatas, Dif
        AssumedDistanceX = NewPos.x - PrevPos.x #X軸距離
        AssumedDistanceY = NewPos.y - PrevPos.y #Y軸距離

        #三平方の定理を使って距離を計算して、math関数で平方根に戻す（xの2乗*yの2乗=zの2乗）
        RobotMillage = math.sqrt(AssumedDistanceX * AssumedDistanceX + AssumedDistanceY * AssumedDistanceY)

        #走行距離計算と小数点以下処理
        if DecimalDigit != -1:
            RobotMillage = round(RobotMillage, DecimalDigit)

            if DecimalDigit == 0:
                RobotMillage = math.floor(RobotMillage)


        #タイヤ回転数と小数点以下処理
        if TireRotationDecimalDigit != -1:
            TireRotation = round(RobotMillage / TireCircumference, TireRotationDecimalDigit)

            if TireRotationDecimalDigit == 0:
                TireRotation = math.floor(TireRotation)

        #進行距離ログを扱いやすいようにリストに格納しておく。いらなければ消す
        
        RobotAngle = 0 #今のみ0にしておく
        #RobotCounter += 1 #カウンター増加
        RobotMillageDatas.append([RobotCounter, NewPos[0], NewPos[1], RobotAngle, RobotMillage, TireRotation])

        if RobotAngle > 180:
            RobotDirection = "左"

        else:
            RobotDirection = "右"
            
        try:
            C_TextEntry1.AppendText("{0}: X:{1} Y:{2} {3}に{4}度 距離:{5}mm タイヤ回転:{6}\n".format(RobotCounter, NewPos[0], NewPos[1], RobotDirection, 0, RobotMillage, TireRotation))

        except:
            Debug("[Info] ControlPanel has been dead.")

        Debug("RobotCounter: {0}".format(RobotCounter))
        Debug("RobotMillage: {0}".format(RobotMillage))
        print(RobotMillageDatas)

    #回転角度（絶対値）取得関数
    def GetDirection(self, PrevPos, NewPos):
        AssumedDistanceX = NewPos.x - PrevPos.x #X軸距離
        AssumedDistanceY = NewPos.y - PrevPos.y #Y軸距離
        
        RobotDegree = math.degrees(math.atan2(AssumedDistanceY, AssumedDistanceX)) #絶対値計算
        Debug("RobotDegree: {0}".format(RobotDegree))
        return RobotDegree

    #クリックを検知する
    def onClick(self, event):
        global PrevPos, NewPos, PrevDeg, NewDeg, RobotCounter
        #カーソル位置取得
        CursorPos = event.GetPosition()

        RobotCounter += 1
        
        #Y座標反転
        DefaultCursorPosY = CursorPos.y
        CursorPos.y = CI_Size.y - CursorPos.y

        Debug("> onClick: ({0}, {1})".format(CursorPos.x, CursorPos.y))
        self.SetStatusText("座標: {0}".format(CursorPos))

        #初回位置かどうか

        if RobotCounter > 1:
            PrevPos = NewPos #一つ前の座標更新
            NewPos = CursorPos #最新座標更新
            PrevDeg = NewDeg #一つ前の角度更新
            NewDeg = self.GetDirection(PrevPos, NewPos)
            Dif = PrevDeg - NewDeg
        else:
            PrevPos = CursorPos
            NewPos = CursorPos
            PrevDeg = 0
            NewDeg = 0
            Dif = 0

        self.MileageCal(PrevPos, NewPos)
        Debug("Dif: {0}".format(Dif))
        
        self.PaintRobot(CursorPos.x, DefaultCursorPosY)

    #ロボット画像描画
    def PaintRobot(self, RobotPosX, RobotPosY):
        global RobotImages

        RobotPosX -= RI_Correct[0]
        RobotPosY -= RI_Correct[1]
        
        RobotImages.append(wx.StaticBitmap(self, wx.ID_ANY, RobotImage.ConvertToBitmap(), pos=(RobotPosX, RobotPosY)))



    #---------------------------------------------------------------------

    #メインウィンドウ（最大化とサイズ変更のみ無効化）
    def __init__(self, title):
        global CI_Size, RobotPanel, RobotImage, RI_Size, RI_Correct
        #global frame
        #frame = wx.Frame(None, -1, "{0} Ver {1}".format(TitleName, Version), size=(WindowSizeX,WindowSizeY), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        wx.Frame.__init__(self, None, -1, title, size=(WindowSizeX,WindowSizeY), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        Panel = wx.Panel(self, wx.ID_ANY)

        #----オブジェクト描画---------------------------------------

        #ツールバー描画
        Menubar = wx.MenuBar()
        FileMenu = wx.Menu()
        FileMenu.Append(1, '新規(&N)\tCtrl+N', '新規のプログラムを作成する')
        FileMenu.Append(2, '開く(&O)\tCtrl+O', '作成したプログラムを開く')
        FileMenu.Append(3, '保存(&S)\tCtrl+S', '作成したプログラムを上書き保存する')
        FileMenu.Append(4, '名前を付けて保存(&A)\tCtrl+A', '作成したプログラムを名前を付けて保存する')
        FileMenu.AppendSeparator()
        FileMenu.Append(5, '終了(&E)\tCtrl+E', 'ソフトウェアを終了する')

        self.Bind(wx.EVT_MENU, self.NewFileCreate, id=1)
        self.Bind(wx.EVT_MENU, self.AskFileOpen, id=2)
        self.Bind(wx.EVT_MENU, self.FileOverWrite, id=3)
        self.Bind(wx.EVT_MENU, self.NewFileSave, id=4)
        self.Bind(wx.EVT_MENU, self.Exit, id=5)
        Menubar.Append(FileMenu, 'ファイル(&F)')
        self.SetMenuBar(Menubar)

        FileMenu2 = wx.Menu()
        FileMenu2.Append(6, '一つ戻す(&Z)\tCtrl+Z', 'プログラムを一つ戻す')
        FileMenu2.Append(7, '全て削除(&U)\tCtrl+U', 'プログラムを白紙に戻す')
        FileMenu2.AppendSeparator()
        FileMenu2.Append(12, 'コントロールパネルを開く(&C)\tCtrl+C', 'コントロールパネルを開く')
        Menubar.Append(FileMenu2, '編集(&E)')
        self.SetMenuBar(Menubar)

        self.Bind(wx.EVT_MENU, self.UndoRobot, id=6)
        self.Bind(wx.EVT_MENU, self.AllRobotsClear, id=7)
        self.Bind(wx.EVT_MENU, self.ControlPanel, id=12)

        FileMenu3 = wx.Menu()
        FileMenu3.Append(13, 'ev3devソースコードに変換(&D)\tCtrl+D', 'プログラムをev3devプログラム（.py）に変換する')
        FileMenu3.Append(14, 'EV3RTソースコードに変換(&R)\tCtrl+R', 'プログラムをEV3RTソースコード（.c）に変換する')
        Menubar.Append(FileMenu3, 'ツール(&T)')

        self.Bind(wx.EVT_MENU, self.ConvertToev3dev, id=13)
        self.Bind(wx.EVT_MENU, self.ConvertToEV3RT, id=14)
        
        self.SetMenuBar(Menubar)


        FileMenu4 = wx.Menu()
        FileMenu4.Append(8, 'オンラインマニュアル(&O)\tCtrl+O', 'このソフトウェアのオンラインマニュアルを表示')
        #FileMenu4.Append(9, 'マニュアル(&H)\tCtrl+H', 'このソフトウェアのオフラインマニュアルを表示')
        FileMenu4.Append(10, 'アップデートのチェック(&U)\tCtrl+U', 'ソフトウェアのアップデートを確認')

        self.Bind(wx.EVT_MENU, self.OnlineUserGuide, id=8)
        #self.Bind(wx.EVT_MENU, self.OfflineUserGuide, id=9)
        self.Bind(wx.EVT_MENU, self.CheckUpdate, id=10)
        FileMenu4.AppendSeparator()

        FileMenu4.Append(11, 'このソフトウェアについて(&A)', 'このソフトウェアの情報を表示します')
        Menubar.Append(FileMenu4, 'ヘルプ(&H)')

        self.Bind(wx.EVT_MENU, self.About, id=11)

        self.SetMenuBar(Menubar)


        #ステータスバー描画
        self.CreateStatusBar()
        #self.SetStatusText("起動完了")

        #キーバインド
        #self.Bind(wx.EVT_KEY_DOWN, self.on_leave_window)

        '''---コート画像描画-----------------------------------------'''

        #コート画像読み込みと貼り付け
        CourtImage = wx.Image(CourtImagePath)

        try:
            os.remove(CourtImagePath)
            
        except:
            Debug("[Error] Could not delete CourtImage.")

        #エラー対策
        try:
            CI_Size = CourtImage.GetSize() #1920x1080用の画像で読み込み

        except Exception as e:
            wx.MessageDialog(None, "回復不能なエラーが発生しました。ソフトウェアを再インストールしてください。\n[Error: CourtImage in the package is missing or corrupt.]", TitleName, style=wx.ICON_ERROR).ShowModal()
            Debug("[Error] Default package is damaged.")
            Debug(e)
            sys.exit()

        Debug("CourtImageSize: {0}".format(CI_Size))

        #コート画像縦横比計算
        CI_Ratio.append(CI_Size[0] / CI_Size[1])
        CI_Ratio.append(CI_Size[1] / CI_Size[0])

        Debug("CourtImageRatio(Calculated): {0}".format(CI_Ratio))

        #CI_Size[0] = (int(format(round(CI_Size[0] * DisplayMagnification, 0), ".0f")))
        #CI_Size[1] = (int(format(round(CI_Size[1] * DisplayMagnification, 0), ".0f")))

        #CI_Size[0] = (int(format(round(CI_Size[0] * 1.405563689604685, 0), ".0f")))
        #CI_Size[1] = (int(format(round(CI_Size[1] * 1.40625, 0), ".0f")))
        
        CI_Size[0] = CI_Size[0] - 28

        Debug("CourtImageReScale: {0}".format(CI_Size))
        CourtImage = CourtImage.Scale(CI_Size[0], CI_Size[1], quality=wx.IMAGE_QUALITY_HIGH)
        #CourtImage = CourtImage.Rescale(600, 250, quality=wx.IMAGE_QUALITY_HIGH)
        #236:225だと思う。
        CI_Bitmap = wx.StaticBitmap(Panel, -1, CourtImage.ConvertToBitmap(), pos=(0, 0), size=CourtImage.GetSize())

        Layout = wx.BoxSizer(wx.VERTICAL)
        Layout2 = wx.BoxSizer(wx.HORIZONTAL)
        Layout2.Add(CI_Bitmap, 1, flag=wx.TOP)
        Layout.Add(Layout2, 1, flag=wx.CENTER)

        #コート画像クリックイベントを取得する関数をBindしておく
        CI_Bitmap.Bind(wx.EVT_LEFT_UP, self.onClick)

        Panel.SetSizer(Layout)

        '''---ロボット画像描画---------------------------------------'''
        
        RobotImage = wx.Image(RobotImagePath)
        RI_Size = RobotImage.GetSize() #○○○x○○○用の画像で読み込み
        RI_Correct.append(int(format(round((RI_Size[0] / 2), 0), '.0f')))
        RI_Correct.append(int(format(round((RI_Size[1] / 2), 0), '.0f')))
        
        Debug("RobotImageSize: {0}".format(RI_Size))
        Debug("RobotImageCorrection: {0}".format(RI_Correct))

        
        self.Show(True)
        self.ControlPanel(True)
        app.SetTopWindow(self)


#メインウィンドウ指定
app = wx.App(False)
MainWindow("{0} Ver {1}".format(TitleName, Version))


#アプリ実行
app.MainLoop()
