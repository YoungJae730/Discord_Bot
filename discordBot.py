import random
import discord
import requests
from discord.ext import commands
from PIL import Image
import io


bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


def getDiceImage(eyes):
    url = "https://upload.wikimedia.org/wikipedia/commons/4/4c/Dice.png"
    res = requests.get(url).content
    im = Image.open(io.BytesIO(res))
    if eyes == 1 :
        return im.crop((0,0,224,224))
    elif eyes == 2 :
        return im.crop((223,0,447,224))
    elif eyes == 3 :
        return im.crop((447,0,671,224))
    elif eyes == 4 :
        return im.crop((0,224,224,448))
    elif eyes == 5 :
        return im.crop((228,224,453,448))
    elif eyes == 6 :
        return im.crop((452,224,676,448))

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()                                                                  #주사위 구현부
async def 주사위(ctx):
    im = Image.new("RGB", (224,224), (255, 255, 255))
    
    im.paste(getDiceImage(random.randrange(1,7)),(0,0))
    
    with io.BytesIO() as image_binary:
        im.save(image_binary, "png")
        image_binary.seek(0)
        out = discord.File(fp=image_binary, filename="dice.png")
        await ctx.reply(file = out)
        
@bot.command()                                                                  # 가위바위보 구현부
async def 가위바위보(ctx):
    dic = {"묵" : "✊", "찌" : "✌️","빠" : "✋"}
    botRSP = random.choice(["묵","찌","빠"])
    class RSPView(discord.ui.View):        
        @discord.ui.select(
            placeholder = "묵 찌 빠!",
            min_values = 1,
            max_values = 1,
            options = [
                discord.SelectOption(
                    label="묵",
                    description="단단한 주먹",
                    emoji="✊"
                ),
                discord.SelectOption(
                    label="찌",
                    description="날카로운 가위",
                    emoji="✌️"
                ),
                discord.SelectOption(
                    label="빠",
                    description="넓은 보자기",
                    emoji="✋"
                ) 
            ]
        )
        async def select_callback(self, interaction, select):
            myEmbed = discord.Embed(title='가위바위보', color=discord.Color.random())
            myEmbed.add_field(name=f"{ctx.message.author.nick}", value=dic[select.values[0]], inline=True)
            myEmbed.add_field(name="Bot", value=dic[botRSP], inline=True)
            if botRSP == select.values[0]:
                myEmbed.set_footer(text="비김")
            elif (botRSP=="묵" and select.values[0]=="찌") or (botRSP=="찌" and select.values[0]=="빠") or (botRSP=="빠" and select.values[0]=="묵"):
                myEmbed.set_footer(text="짐")
            else:
                myEmbed.set_footer(text="이김")
            await interaction.response.edit_message(view=None, embed=myEmbed)
    
    msg = await ctx.reply("묵 찌 빠!", view=RSPView())

@bot.command()                                                                  # 숫자맞추기 구현부
async def 숫자맞추기(ctx, ranges=0, choiCnt=50):
    if ranges>1 & ranges<=25:    
        ans = random.randrange(1,ranges+1)
        cnt = 0
        
        class UpDown(discord.ui.View):                                          
            cnt = 0
            numbers = []
            for i in range(ranges):
                numbers.append(
                    discord.SelectOption(
                        label=i+1,
                        description=f"{i+1} 선택"
                    ))
            @discord.ui.select(
                    placeholder = "숫자를 선택해 주세요",
                    min_values = 1,
                    max_values = 1,
                    options = numbers
            )
            async def select_callback(self, interaction, select):
                UpDown.cnt += 1
                if int(select.values[0])==ans:
                    await interaction.response.edit_message(content=f"{ans} 정답! / 시도 횟수 : {UpDown.cnt}", view=None)
                    UpDown.cnt = 0
                elif int(select.values[0])<ans:          
                    if UpDown.cnt>=choiCnt:
                        await interaction.response.edit_message(content=f"실패! / 정답 : {ans} / 시도 횟수 : {UpDown.cnt}", view=None)
                    else:
                        await interaction.response.edit_message(content=f"업  / 시도 횟수 : {UpDown.cnt}")
                elif int(select.values[0])>ans:
                    if UpDown.cnt>=choiCnt:
                        await interaction.response.edit_message(content=f"실패! / 정답 : {ans} / 시도 횟수 : {UpDown.cnt}", view=None)
                    else:
                        await interaction.response.edit_message(content=f"다운/ 시도 횟수 : {UpDown.cnt}")
                    
        await ctx.reply("숫자맞추기", view=UpDown())
    else:
        await ctx.reply("사용 방법: !숫자맞추기  [숫자(2~25)]  [횟수제한(생략시 무제한)]")
        
@bot.command()                                                                  # 블랙잭 구현부
async def 블랙잭(ctx):
    deck=[]                                                                     # 카드덱 설정부
    nums=['A','2','3','4','5','6','7','8','9','10','J','Q','K']
    shapes=['Spade','Diamond','Heart','Clover']
    
    for shape in shapes:
        for num in nums:
            deck.append(num + ' ' + shape)

    random.shuffle(deck)                                                        # 카드덱 셔플
    
    player_hand=[deck.pop(),deck.pop()]                                         # 플레이어 핸드 2개 뽑기
    dealer_hand=[deck.pop(),deck.pop()]                                         # 딜러 핸드 2개 뽑기
    
    def calculate_hand(hand):                                                   # 핸드 카드 점수 계산
        score=0
        num_aces=0
        for card in hand:
            num = card.split()[0]
            if num == 'A':
                num_aces += 1
                score += 11
            elif num in ['J','Q','K']:
                score += 10
            else:
                score += int(num)
        while num_aces > 0 and score > 21:
            score -= 10
            num_aces -= 1
        return score
    
    myEmbed = discord.Embed(title='블랙잭', color=discord.Color.random())       # 출력 메세지 설정
    myEmbed.add_field(name="딜러", value=','.join(s for s in dealer_hand)+f' 점수 : {calculate_hand(dealer_hand)}', inline=False)
    myEmbed.add_field(name=f"유저 : {ctx.message.author.nick}", value=', '.join(s for s in player_hand)+f' 점수 : {calculate_hand(player_hand)}', inline=True)
    
    class button(discord.ui.View):
        @discord.ui.button(label='Hit', row=1, custom_id='hit')                 # hit 버튼 구현 부분
        async def button1_callback(self, interaction, button):
            player_hand.append(deck.pop())
            changedEmbed = discord.Embed(title='블랙잭', color=discord.Color.random())
            changedEmbed.add_field(name="딜러", value=','.join(s for s in dealer_hand)+f' 점수 : {calculate_hand(dealer_hand)}', inline=False)
            
            if calculate_hand(player_hand) == 21:
                changedEmbed.add_field(name=f"유저 : {ctx.message.author.nick}", value=', '.join(s for s in player_hand)+f' 점수 : {calculate_hand(player_hand)} 블랙잭!', inline=True)
                changedEmbed.set_footer(text=f'{ctx.message.author.nick}님의 승리')
                await interaction.response.edit_message(embed=changedEmbed, view=None)
            elif calculate_hand(player_hand) > 21:
                changedEmbed.add_field(name=f"유저 : {ctx.message.author.nick}", value=', '.join(s for s in player_hand)+f' 점수 : {calculate_hand(player_hand)} 버스트!', inline=True)
                changedEmbed.set_footer(text=f'{ctx.message.author.nick}님의 패배')
                await interaction.response.edit_message(embed=changedEmbed, view=None)
            else:
                changedEmbed.add_field(name=f"유저 : {ctx.message.author.nick}", value=', '.join(s for s in player_hand)+f' 점수 : {calculate_hand(player_hand)}', inline=True)
                await interaction.response.edit_message(embed=changedEmbed)
            
        @discord.ui.button(label='Stand', row=1, custom_id='stand')             # stand 버튼 구현 부분
        async def button2_callback(self, interaction, button):
            while calculate_hand(dealer_hand) < 17:
                dealer_hand.append(deck.pop())
            changedEmbed = discord.Embed(title='블랙잭', color=discord.Color.random())
            
            dealer_score = calculate_hand(dealer_hand)
            player_score = calculate_hand(player_hand)
            
            if dealer_score > 21:                                               
                changedEmbed.add_field(name="딜러", value=','.join(s for s in dealer_hand)+f' 점수 : {dealer_score} 버스트!', inline=False)
                changedEmbed.add_field(name=f"유저 : {ctx.message.author.nick}", value=', '.join(s for s in player_hand)+f' 점수 : {player_score}', inline=True)
                changedEmbed.set_footer(text=f'{ctx.message.author.nick}님의 승리')
                await interaction.response.edit_message(embed=changedEmbed, view=None)
            elif player_score > dealer_score:
                changedEmbed.add_field(name="딜러", value=','.join(s for s in dealer_hand)+f' 점수 : {dealer_score}', inline=False)
                changedEmbed.add_field(name=f"유저 : {ctx.message.author.nick}", value=', '.join(s for s in player_hand)+f' 점수 : {player_score}', inline=True)
                changedEmbed.set_footer(text=f'{ctx.message.author.nick}님의 승리')
                await interaction.response.edit_message(embed=changedEmbed, view=None)
            elif player_score < dealer_score:
                changedEmbed.add_field(name="딜러", value=','.join(s for s in dealer_hand)+f' 점수 : {dealer_score}', inline=False)
                changedEmbed.add_field(name=f"유저 : {ctx.message.author.nick}", value=', '.join(s for s in player_hand)+f' 점수 : {player_score}', inline=True)
                changedEmbed.set_footer(text=f'{ctx.message.author.nick}님의 패배')
                await interaction.response.edit_message(embed=changedEmbed, view=None)
            else:
                changedEmbed.add_field(name="딜러", value=','.join(s for s in dealer_hand)+f' 점수 : {dealer_score}', inline=False)
                changedEmbed.add_field(name=f"유저 : {ctx.message.author.nick}", value=', '.join(s for s in player_hand)+f' 점수 : {player_score}', inline=True)
                changedEmbed.set_footer(text=f"푸시! 유저 {ctx.message.author.nick}님의 패배")
                await interaction.response.edit_message(embed=changedEmbed, view=None)
            
    await ctx.reply(embed=myEmbed, view=button())

bot.run('코드')
