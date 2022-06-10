import discord
from discord.ext import commands
import asyncio
import os
from github import Github

bot = commands.Bot(command_prefix='$')

bot_token = os.environ['bot']
github_token = os.environ['github']

g = Github(github_token);
repo = g.get_repo(int(os.environ['repo_id']))

latest_id = repo.get_latest_release().id;

class AsyncCounter:
    def __init__(self, stop):
        self.current = 0
        self.stop = stop

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current < self.stop:
            await asyncio.sleep(0.2)
            r = self.current
            self.current += 1
            return r
        else:
            raise StopAsyncIteration

async def check_update():
    while True:
        check = repo.get_latest_release().id;
        global latest_id
        if check > latest_id:
            await send_update()
            latest_id = check
        await asyncio.sleep(1.5)
    
async def send_update():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            bot_member = get_bot(channel)
            if bot_member != None and channel.permissions_for(bot_member).send_messages:
                try:
                    latest = repo.get_latest_release()
                    await channel.send('코크스 애드온 %s 업데이트입니다.'%(latest.title))
                    splited = split_string(latest.body)
                    async for i in AsyncCounter(len(splited)):
                        await channel.send('```%s```'%(splited[i]))
                except:
                    continue
                
def get_bot(channel: discord.TextChannel):
    for member in channel.members:
        try:
            if member.id == 812320103617134614:
                return member
        except AttributeError:
            continue
    return None

@bot.event
async def on_ready():
    game = discord.Game("코크스 애드온 소식 전달")
    await bot.change_presence(status=discord.Status.online, activity=game)
    bot.loop.create_task(check_update())
    
def split_string(body: str):
    split_strings = body.split("\n")
    result = []
    temp = "";
    for string in split_strings:
        if (len(temp) + len(string) > 1994):
            result.append(temp)
            temp = ""
            
        if temp == "": temp = string
        else: temp += ("\n"+string)
        
    result.append(temp)
    return result
    
bot.run(bot_token)