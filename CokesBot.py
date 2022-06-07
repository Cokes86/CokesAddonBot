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

async def github_send():
    while True:
        check = repo.get_latest_release().id;
        global latest_id
        if check > latest_id:
            await send_latest_version_all()
            latest_id = check
        await asyncio.sleep(2)
        
async def send_latest_version(channel: discord.TextChannel):
    latest = repo.get_latest_release()
    await channel.send('코크스 애드온 %s 업데이트입니다.'%(latest.title))
    
    async for send_message in split_string(latest.body):
        await channel.send('```%s```'%(send_message))
    
async def send_latest_version_all():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            bot_member = get_bot(channel)
            if bot_member != None and channel.permissions_for(bot_member).send_messages:
                await send_latest_version(channel)
                
def get_bot(channel: discord.TextChannel):
    for member in channel.members:
        print(member.name)
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
    bot.loop.create_task(github_send())
    
async def split_string(body: str):
    split_strings = body.split("\n")
    result = []
    temp = "";
    for string in split_strings:
        lens = len(string.encode("UTF-8"));
        if (len(temp.encode("UTF-8")) + lens > 2000):
            result.append(temp)
            temp = ""
            
        if temp == "": temp = string
        else: temp += ("\n"+string)
        
    result.append(temp)
    return result

    
bot.run(bot_token)