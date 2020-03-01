from discord.ext import commands # Bot Commands Frameworkのインポート
import discord
import random

# エラーリスト
ERROR_CODE = list()

# コグとして用いるクラスを定義。
class DiceCog(commands.Cog):

    # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    # コマンドの作成。コマンドはcommandデコレータで必ず修飾する。
    @commands.command()
    async def dicetest(self, ctx, *dice):
        print(dice)
        dice_analyze = command_analyze(list(dice))
        await ctx.send('DICE ROLLING...')
        
    # ノーマルダイス　結果だけ返却します
    @commands.command(aliases=['rs'])
    async def rollsimple(self, ctx, *dice):
        # コマンド解析
        dice_analyze = command_analyze(list(dice))
        print(dice_analyze)
        
        error = error_check()
        if(error != ""):
            await ctx.send(error)
            return 0
        
        # ダイスを振る
        roll_result = roll_dice(str(dice[0]))
        
        if('ineq' in dice_analyze.keys()):
            diff_res = diffcheck(sum(roll_result), dice_analyze['ineq'], int(dice_analyze['base']))
        if('crit' in dice_analyze.keys()):
            crit_res = critcheck(sum(roll_result), dice_analyze['crit_hit_ineq'], dice_analyze['crit_hit_base'], dice_analyze['crit_split_ineq'], dice_analyze['crit_split_base'])
        
        # リザルト出力
        result_text = 'RESULT: '+ str(sum(roll_result))
        
        if('ineq' in dice_analyze.keys()):
            result_text += diff_res
        if('crit_hit_ineq' in dice_analyze.keys()):
            result_text += crit_res
        
        await ctx.send(result_text)
    
    # 詳細ダイス　出目もすべて返却します
    @commands.command(aliases=['r'])
    async def roll(self, ctx, *dice):
        # コマンド解析
        dice_analyze = command_analyze(list(dice))
        print(dice_analyze)
        
        error = error_check()
        if(error != ""):
            await ctx.send(error)
            return 0
        
        # ダイスを振る
        roll_result = roll_dice(str(dice[0]))
        
        if('ineq' in dice_analyze.keys()):
            diff_res = diffcheck(sum(roll_result), dice_analyze['ineq'], int(dice_analyze['base']))
        if('crit' in dice_analyze.keys()):
            crit_res = critcheck(sum(roll_result), dice_analyze['crit_hit_ineq'], dice_analyze['crit_hit_base'], dice_analyze['crit_split_ineq'], dice_analyze['crit_split_base'])
        
        # リザルト出力
        result_text = 'RESULT: '+ str(sum(roll_result))
        
        if('ineq' in dice_analyze.keys()):
            result_text += diff_res
        if('crit_hit_ineq' in dice_analyze.keys()):
            result_text += crit_res
        
        await ctx.send(roll_result)
        await ctx.send(result_text)
    

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(DiceCog(bot)) # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する。
    

# コマンド解析
def command_analyze(dice):
    # 返り値の初期化(ディクショナリ)
    dice_analyze = {}
    
    # 0ダイスならエラー
    if(dice[0].find('d0') != -1):
        ERROR_CODE.append("DICE_ZERO_ERROR")
    else:
        # 一つ目にnDaを入れる
        dice_analyze['dice_str'] = dice[0].lower()
    
    # 20個までNoneで満たす
    dicearray = fillArray(dice)
    
    if ('+' in dicearray):
        calc_index = dicearray.index('+')
        calc_point = dicearray[calc_index + 1]
        if (calc_point.isnumeric() == true):
            dice_analyze['calc_mark'] = '+'
            dice_analyze['calc_point'] = calc_point
        else:
            ERROR_CODE.append("CALC_ERROR")
    if ('-' in dicearray):
        calc_index = dicearray.index('-')
        calc_point = dicearray[calc_index + 1]
        if (calc_point.isnumeric() == true):
            dice_analyze['calc_mark'] = '-'
            dice_analyze['calc_point'] = calc_point
        else:
            ERROR_CODE.append("CALC_ERROR")
    
    # クリティカルトリガーを検索　※ただの不等式と併用不可
    if ('crit' in dicearray):
        crit_index = dicearray.index('crit')
        crit_hit_ineq = dicearray[crit_index + 1]
        crit_hit_base = dicearray[crit_index + 2]
        crit_split_ineq = dicearray[crit_index + 3]
        crit_split_base = dicearray[crit_index + 4]
        if(crit_hit_ineq == None or crit_hit_base == None or crit_split_ineq == None or crit_split_base == None):
            ERROR_CODE.append("CRIT_PARAM_ERROR")
        else:
            dice_analyze['crit_hit_ineq'] = crit_hit_ineq
            dice_analyze['crit_hit_base'] = crit_hit_base
            dice_analyze['crit_split_ineq'] = crit_split_ineq
            dice_analyze['crit_split_base'] = crit_split_base
    else: 
        # 不等式トリガーを検索　※クリティカルとカブらないようelseに配置
        if  ('<' in dicearray):
            ineq = '<'
            base_index = dicearray.index('<')
            base = dicearray[base_index + 1]
            if(base == None):
                ERROR_CODE.append("NOT_BASE_EXIST")
            else:
                dice_analyze['ineq'] = ineq
                dice_analyze['base'] = base
        elif('>' in dicearray):
            ineq = '>'
            base_index = dicearray.index('>')
            base = dicearray[base_index + 1]
            if(base == None):
                ERROR_CODE.append("NOT_BASE_EXIST")
            else:
                dice_analyze['ineq'] = ineq
                dice_analyze['base'] = base
        elif('<=' in dicearray):
            ineq = '<='
            base_index = dicearray.index('<=')
            base = dicearray[base_index + 1]
            if(base == None):
                ERROR_CODE.append("NOT_BASE_EXIST")
            else:
                dice_analyze['ineq'] = ineq
                dice_analyze['base'] = base
        elif('>=' in dicearray):
            ineq = '>='
            base_index = dicearray.index('>=')
            base = dicearray[base_index + 1]
            if(base == None):
                ERROR_CODE.append("NOT_BASE_EXIST")
            else:
                dice_analyze['ineq'] = ineq
                dice_analyze['base'] = base
    
    return dice_analyze

# ダイスロール本体
def roll_dice(dice):
    
    roll_point_list = []
    
    # dの小文字大文字両対応
    dicestring = dice.lower()
    
    roll_times = dicestring.split("d")[0]
    dice_size  = dicestring.split("d")[1]
    
    if(dice_size == ""):
        dice_size = 6

    for i in range(int(roll_times)):
        roll_point_list.append(random.randrange(1,int(dice_size)+1))
    
    return roll_point_list

# 比較部分
def diffcheck(roll_result, ineq, base):
    # 成功/失敗を判定
    if ineq == '<':
        if roll_result < base:
            return ' 成功！'
        else:
            return ' 失敗...'
    elif ineq == '>':
        if roll_result > base:
            return ' 成功！'
        else:
            return ' 失敗...'
    elif ineq == '<=':
        if roll_result <= base:
            return ' 成功！'
        else:
            return ' 失敗...'
    elif ineq == '>=':
        if roll_result >= base:
            return ' 成功！'
        else:
            return ' 失敗...'
    else:
        return 'チート使うなハゲ'
    

def critcheck(roll_result, hit_ineq, hit_base, split_ineq, split_base):
    # 決定的成功判定
    if hit_ineq == '<':
        if roll_result < hit_base:
            return ' 決定的成功！'
    if hit_ineq == '>':
        if roll_result > hit_base:
            return ' 決定的成功！'
    if hit_ineq == '<=':
        if roll_result <= hit_base:
            return ' 決定的成功！'
    if hit_ineq == '>=':
        if roll_result >= hit_base:
            return ' 決定的成功！'
    
    # 致命的失敗判定
    if split_ineq == '<':
        if roll_result < split_base:
            return ' 致命的失敗...'
    if split_ineq == '>':
        if roll_result > split_base:
            return ' 致命的失敗...'
    if split_ineq == '<=':
        if roll_result <= split_base:
            return ' 致命的失敗...'
    if split_ineq == '>=':
        if roll_result >= split_base:
            return ' 致命的失敗...'

# コマンド引数を20まで増やしてNoneのエラーを回避する
def fillArray(array):
    arraylen = len(array)
    if arraylen > 20:
        print('コマンド引数が多すぎます')
        return array
    for i in range(20 - arraylen):
        array.append(None)
    
    return array

def error_check():
    error_res = ""
    if('NOT_BASE_EXIST' in ERROR_CODE):
        error_res += " 不等式の比較する数を指定してください"
    if('CRIT_PARAM_ERROR' in ERROR_CODE):
        error_res += " critコマンド引数を確認してください"
    if('DICE_ZERO_ERROR' in ERROR_CODE):
        error_res += " 出目が0のダイスは振れません"
    if('CALC_ERROR' in ERROR_CODE):
        error_res += " 計算項目が不正です"
    return error_res
