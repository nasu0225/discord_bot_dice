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
class DiceTool(commands.Cog):
    #__init__
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['r'])
    async def roll(self, ctx, *dice):
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
            
            # 保持した値を検索し置き換える
            # DEBUG:
            expandDice = dice
            forError = ' '.join(map(str, expandDice))
            
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
    
    # @commands.command()
    # async def set(self, ctx, *str):
    
    # @commands.command()
    # async def test(self, ctx, *str):
    #     currentdir = os.getcwd()
    #     await ctx.send(currentdir)

# [パーツ]=======================================================================

# Bot本体側からコグを読むときの関数
def setup(bot):
    # Botにコグとして登録
    bot.add_cog(DiceTool(bot))

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
