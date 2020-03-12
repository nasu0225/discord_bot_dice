from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
import random
import re
import csv
import pprint
import os

# [ERROR CLASS]=================================================================
class RollError(Exception):
    pass

# やること
# keyと文字列を記憶して、簡単に振れるようにする($diceset axe 3d + 1)->($r axe)とか
# エラーコレクトきっちりやる
# 作り忘れてる部分を探してなんかうまいことやる

# [本体]========================================================================
class DiceCog(commands.Cog):
    #__init__
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['r'])
    async def roll(self, ctx, *dice):
        """\nサイコロを振る(略式：r)\n例：$r 1d6 引数を略すと例と同値に扱われます。\nダイスの面数を略すと6面ダイスになります。\nsetコマンドで設定した略式を利用できます。\n"""
        # 初期化
        global ERROR_CODE
        ERROR_CODE = {}
        dice = list(dice)
        msg = ""
        error = ""
        
        try:
            # 省略表記に対応
            if(len(dice) == 0):
                dice.append("1d6")
            
            # DEBUG:
            expandDice = dice
            forError = ' '.join(map(str, expandDice))
            
            # 保持した値を検索し置き換える
            expandDice = convertKey(expandDice)
            
            # ダイスを振る
            rolledDiceCom = rollDiceComArray(expandDice)
            
            # 数字に戻す
            calcCom = setRollResultToCom(expandDice, rolledDiceCom)
            
            # 加算・減算
            resultDice = getCalcDice(calcCom)
            msg += str(resultDice)
            
            # メンションを設定
            mention = ctx.author.mention
            
        except SyntaxError as Err:
            await ctx.send('構文エラーです。コマンドを確認してください。\n'+'コマンド :'+ forError +'\n')
            return 0
        
        except NameError as Err:
            await ctx.send(Err)
            return 0
        
        except RollError as Err:
            await ctx.send(Err)
            return 0
        
        print(rolledDiceCom)
        msg += '\n'
        for i, value in enumerate(rolledDiceCom):
            print(rolledDiceCom[value])
            msg += '['+','.join(map(str, rolledDiceCom[value]))+'] '
        await ctx.send('RESULT: '+msg+'\n'+mention)
    
    @commands.command()
    async def set(self, ctx, *rec):
        """\nrollコマンドで利用できる略式を設定できます。\n例：$set sample 1d6 -> $r sampleと入力すると$r 1d6と同値と扱われます。"""
        # メンションを設定
        mention = ctx.author.mention
        try:
            rec = list(rec)
            # recの最初の値はKeyになる
            key = rec.pop(0)+' '
            
            # Keyはダイスまたは数式に沿う文字列に対応しません
            if(re.fullmatch(r'([0-9]*d+[0-9]*)', key) or re.fullmatch(r'[0-9]*', key)):
                raise RollError('キーはダイス又は数式の形式を取る文字列に対応しません')
            # Keyを取得、比較
            keylist = keycheck()
            if not (keyDupCheck(keylist, key)):
                raise RollError('キーが重複しています。')
            
            com = ' '.join(map(str, rec))
            # 無効な数式 ※ダイスを振ってみて問題なければOK → 記号とかで終わる式には今の所対応しません
            rolledDiceCom = rollDiceComArray(rec)
            calcCom = setRollResultToCom(rec, rolledDiceCom)
            resultDice = getCalcDice(calcCom)
            
            setCommand = [key[:-1],com]
            with open('record.csv', 'a', newline="") as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow(setCommand)
        
        except RollError as Err:
            await ctx.send(str(Err)+'\n'+mention)
            return 0
            
        except NameError as Err:
            await ctx.send(Err)
            return 0
            
        except SyntaxError as Err:
            await ctx.send('構文エラーです。コマンドを確認してください。\n'+'コマンド :'+ str(com) +'\n')
            return 0
    
    @commands.command()
    async def keydelete(self, ctx, key):
        """\nsetコマンドで設定したキーを削除します"""
        keyList = []
        with open('record.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                if not(key == row[0]):
                    keyList.append(row)
        print(keyList)
        
        with open('record.csv', 'w', newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerows(keyList)
    
    @commands.command()
    async def get(self, ctx, *a):
        """\nsetコマンドで設定したキーの一覧を表示します"""
        with open('record.csv') as f:
            await ctx.send(f.read())
    
    @commands.command()
    async def check(self, ctx, *a):
        """\n管理用：setコマンドで設定するキーを保持するファイルの確認をします"""
        try:
            with open('record.csv', mode='x') as f:
                f.write('')
            await ctx.send('ファイルを作成しました')
        except FileExistsError:
            await ctx.send('ファイルは存在しています。\n初期化する場合はresetコマンドを使用してください')
    
    @commands.command()
    async def reset(self, ctx, a):
        """\n管理用：setコマンドで設定するキーを保持するファイルを初期化します\n※パスワードを設定してあります"""
        try:
            a = str(a)
            if not(a == 'reset'):
                raise RollError('パスワードが違います')
            
            shutil.copy('record.csv', 'record.csv.bac')
            with open('record.csv', 'w') as f:
                f.write('')
            await ctx.send('ファイルを初期化しました')
        
        except RollError as Err:
            await ctx.send(Err)
    
    @commands.command()
    async def restore(self, ctx, a):
        """\n管理用：resetしたファイルを戻します\n※パスワードを設定してあります"""
        try:
            a = str(a)
            if not(a == 'reset'):
                raise RollError('パスワードが違います')
            
            shutil.move('record.csv.bac', 'record.csv')
            await ctx.send('リストアしました')
        
        except RollError as Err:
            await ctx.send(Err)

# [パーツ]=======================================================================

# Bot本体側からコグを読むときの関数
def setup(bot):
    # Botにコグとして登録
    bot.add_cog(DiceCog(bot))

# パラメータのうちダイスをロールする
def rollDiceComArray(com_list):
    dice_result = {}
    for index in range(len(com_list)):
        s = str(com_list[index])
        a = re.fullmatch(r'[0-9]*d[0-9]*', s)
        if(a != None):
            dice_result[index] = rollDice(com_list[index]) 
    
    return dice_result
    
# ダイスロール本体
def rollDice(dice):
    
    roll_point_list = []
    
    # dの小文字大文字両対応
    dicestring = dice.lower()
    
    roll_times = dicestring.split("d")[0]
    dice_size  = dicestring.split("d")[1]
    
    if(dice_size == ""):
        dice_size = 6
    
    if(len(roll_times) == 0):
        roll_times = 1
    if(dice_size == 0):
        raise RollError("ダイスを0回振ることはできません")

    for i in range(int(roll_times)):
        roll_point_list.append(random.randrange(1,int(dice_size)+1))
    
    return roll_point_list

# コマンド引数にダイス結果を使って数字に戻す
def setRollResultToCom(dice, roll):
    for key in roll:
        dice[key] = sum(roll[key])
    
    return dice

def getCalcDice(com):
    # 足し算or引き算しか使えないようにする
    com = list(map(str, com))
    joincom = ' '.join(com) + ' '
    
    if(re.fullmatch(r'([0-9]* +[+-]? *[0-9]*)+', joincom)):
        a = eval(joincom)
    else:
        raise RollError('適さない数式が入力されました。コマンドを確認して下さい。')
    
    return a

# CSVファイルから全Keyを取得して返却
def keycheck():
    keyList = []
    with open('record.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            keyList.append(row[0])
    return keyList

# 被りがなければTrue,あればFlaseを返却
def keyDupCheck(keylist, key):
    for checker in keylist:
        if(key == checker):
            return False
    return True

# ダイスコマンドのキーになる部分をダイスコマンドに変換する
def convertKey(comlist):
    conv = {}
    print(comlist)
    with open('record.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            i = 0
            for com in comlist:
                if (com == row[0]):
                    conv[i] = row[1]
                i += 1
    for a in conv:
        del comlist[a]
        comlist[a:a] = conv[a].split()
    return comlist
    
