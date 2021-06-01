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


#変数定義群
TitleName = "NavigationEV3 ReWrite" #タイトル名
Version = "3.0.0α-Dev8" #バージョン
Developer = "© 2020-2021 Kenta Sui"

DisplayMax = [1920, 1080]
DisplayMin = [1280, 720]
WindowRatio = [16, 9]
SubWindowSize = [550, 480]

FontSize = 10
ConfigPath = "Config/Config.ini"

DebugOutput = True #デバッグ情報を出力するか

DefaultHomePath = "C:"
DefaultCourtImagePath = "Data/New2.png"
DefaultRobotImagePath = "Data/Robot.png"

UserGuideURL = "https://zcen.net"
UserGuidePath = "Data/UserGuide.txt"

'''----定義・初期設定等---------------------------------------'''

#リストの定義
DisplaySize = []
WindowSize = []
CI_Ratio = []

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
Debug("SubWindowSize: {0}".format(SubWindowSize))
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

#Config読み込み（try exceptで対策必要）
ConfigLoader.read(ConfigPath, encoding="utf-8")
Config = ConfigLoader["Settings"]
Debug("\n> The configuration file has been successfully loaded.")
Debug("\n--User defined constants(Config)--")

WindowSizeScale = float(format(float(Config.get("Zoom")), ".2f")) #ウィンドウ表示倍率
CourtImagePath = str(Config.get("CourtImagePath")) #コート画像パス
RobotImagePath = str(Config.get("RobotImagePath")) #ロボット画像パス
HomePath = str(Config.get("HomePath")) #ホームディレクトリ
Debug("WindowSizeScale: {0}".format(WindowSizeScale))
Debug("CourtImagePath: {0}".format(CourtImagePath))
Debug("RobotImagePath: {0}".format(RobotImagePath))
Debug("HomePath: {0}".format(HomePath))

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


#ホームディレクトリ取得（ユーザー）
HomeDirectory = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\" + HomePath

#指定されたディレクトリが
if not os.path.exists(HomeDirectory):
    HomeDirectory = DefaultHomePath
    Debug("[Error] The specified path could not be found. Use the default directory.")

elif not os.path.isdir(HomeDirectory):
    HomeDirectory = DefaultHomePath
    Debug("[Error] The specified path is not a directory. Use the default directory.")

Debug("HomeDirectory: {0}".format(HomeDirectory))


'''---ウィンドウ別クラス（メイン）----------------------------------------'''

#ソフトウェアについてタブ
class AboutWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(SubWindowSize), style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

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


#メインウィンドウ
class MainWindow(wx.Frame):
        
    #---関数------------------------------------------

    #退出用
    def Exit(self, event):
        sys.exit(0)

    #ファイルオープン
    def AskFileOpen(self, event):
        FileTypes = "NavigationEV3 ReWrite ファイル (*.nrf) |*.nrf|" "すべてのファイル (*.*) |*.*"
        OpenFileDialog = wx.FileDialog(frame, message="開く", wildcard=FileTypes, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        #ユーザーがキャンセルした場合、スルー
        if OpenFileDialog.ShowModal() != wx.ID_OK:
            return

        OpenFilePath = OpenFileDialog.GetPath()
        wx.MessageDialog(None, "あなたの選択した読み込みファイル\n{0}\n※読み込み機能は未実装です".format(OpenFilePath), TitleName).ShowModal()
        OpenFileDialog.Destroy()

    #新規ファイルオープン
    def NewFileCreate(self, event):
        wx.MessageDialog(None, "未実装です", TitleName).ShowModal()

    #ファイル上書き
    def FileOverWrite(self, event):
        wx.MessageDialog(None, "未実装です", TitleName).ShowModal()

    #ファイルの名前を付けて保存
    def NewFileSave(self, event):
        FileTypes = "NavigationEV3 ReWrite ファイル (*.nrf) |*.nrf|" "すべてのファイル (*.*) |*.*"
        SaveFileDialog = wx.FileDialog(frame, message="名前を付けて保存", wildcard=FileTypes, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        #ユーザーがキャンセルした場合、スルー
        if SaveFileDialog.ShowModal() != wx.ID_OK:
            return

        SaveFilePath = SaveFileDialog.GetPath()
        wx.MessageDialog(None, "あなたの選択した保存先\n{0}\n※保存機能は未実装です".format(SaveFilePath), TitleName).ShowModal()
        SaveFileDialog.Destroy()

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


    #---------------------------------------------------------------------

    #メインウィンドウ（最大化とサイズ変更のみ無効化）
    def __init__(self, title):
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
        Menubar.Append(FileMenu2, '編集(&E)')
        self.SetMenuBar(Menubar)

        FileMenu3 = wx.Menu()
        FileMenu3.Append(8, 'オンラインマニュアル(&O)\tCtrl+O', 'このソフトウェアのオンラインマニュアルを表示')
        #FileMenu3.Append(9, 'マニュアル(&H)\tCtrl+H', 'このソフトウェアのオフラインマニュアルを表示')
        FileMenu3.Append(10, 'アップデートのチェック(&U)\tCtrl+U', 'ソフトウェアのアップデートを確認')

        self.Bind(wx.EVT_MENU, self.OnlineUserGuide, id=8)
        #self.Bind(wx.EVT_MENU, self.OfflineUserGuide, id=9)
        FileMenu3.AppendSeparator()

        FileMenu3.Append(11, 'このソフトウェアについて(&A)', 'このソフトウェアの情報を表示します')
        Menubar.Append(FileMenu3, 'ヘルプ(&H)')

        self.Bind(wx.EVT_MENU, self.About, id=11)

        self.SetMenuBar(Menubar)

        #ステータスバー描画
        self.CreateStatusBar()
        #self.SetStatusText("起動完了")

        '''---コート画像描画-----------------------------------------'''

        #コート画像読み込みと貼り付け
        CourtImage = wx.Image(CourtImagePath)
        CI_Size = CourtImage.GetSize() #1920x1080用の画像で読み込み
        Debug("CourtImageSize: {0}".format(CI_Size))

        #コート画像縦横比計算
        CI_Ratio.append(CI_Size[0] / CI_Size[1])
        CI_Ratio.append(CI_Size[1] / CI_Size[0])

        Debug("CourtImageRatio(Calculated): {0}".format(CI_Ratio))

        #CI_Size[0] = (int(format(round(1920 / CI_Ratio[0], 0), ".0f")))
        #CI_Size[1] = (int(format(round(1080 / CI_Ratio[1], 0), ".0f")))
        CI_Size[0] = CI_Size[0] - 28

        Debug("CourtImageReScale: {0}".format(CI_Size))
        CourtImage = CourtImage.Scale(CI_Size[0], CI_Size[1], quality=wx.IMAGE_QUALITY_HIGH)
        #CourtImage = CourtImage.Rescale(1076, 531, quality=wx.IMAGE_QUALITY_HIGH)
        #236:225だと思う。
        CI_Bitmap = wx.StaticBitmap(Panel, -1, CourtImage.ConvertToBitmap(), pos=(0, 0), size=CourtImage.GetSize())

        Layout = wx.BoxSizer(wx.VERTICAL)
        Layout2 = wx.BoxSizer(wx.HORIZONTAL)
        Layout2.Add(CI_Bitmap, 1, flag=wx.TOP)
        Layout.Add(Layout2, 1, flag=wx.CENTER)

        Panel.SetSizer(Layout)

        '''---ロボット画像描画---------------------------------------'''

        #コート画像読み込みと貼り付け
        '''RobotImage = wx.Image(RobotImagePath)
        RI_Size = RobotImage.GetSize() #○○○x○○○用の画像で読み込み
        Debug("RobotImageSize: {0}".format(RI_Size))

        RI_Size[0] = int(format(round(RI_Size[0] / DisplayMagnification, 0), ".0f"))
        RI_Size[1] = int(format(round(RI_Size[1] / DisplayMagnification, 0), ".0f"))
        Debug("RobotImageReScale: {0}".format(RI_Size))
        
        RobotImage = RobotImage.Rescale(RI_Size[0], RI_Size[1], quality=wx.IMAGE_QUALITY_HIGH)
        RI_Bitmap = wx.StaticBitmap(Panel, -1, RobotImage.ConvertToBitmap(), pos=(0, 0), size=RobotImage.GetSize())'''
     
        self.Show(True)
        app.SetTopWindow(self)


#メインウィンドウ指定
app = wx.App(False)
MainWindow("{0} Ver {1}".format(TitleName, Version))


#アプリ実行
app.MainLoop()
