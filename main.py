# boilerplate discord bot code
import os
import discord
import requests
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

# GUILD = os.getenv('DISCORD_GUILD')
TOKEN = os.getenv("DISCORD_TOKEN")
BUG_REPORTS_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True


# Initialize Bot and Denote The Command Prefix
bot = commands.Bot(command_prefix="!", allowed_mentions=discord.AllowedMentions(everyone=True), intents=intents)


# Runs when Bot Succesfully Connects
@bot.event
async def on_ready():
    print(f'{bot.user} succesfully logged in!')
    # channel = bot.get_channel(1041720326125518878)
    # await channel.send("Hello")


# sends messages when detecting certain words
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)
@bot.event
async def on_thread_create(thread):
    if thread.channel.id == BUG_REPORTS_CHANNEL_ID:
        issueUrl = await createGithubIssue(thread.name, thread.starter_message.content)
        if issueUrl is not None:
            await thread.send(f"Created issue on GitHub: {issueUrl}")



# sends description of each command
#@bot.command()
#async def commands(ctx):
#    print("Received")
#    await ctx.send(f"""$dance: does a fun little dance (no stuff needed)
#$uwu: OWO-uuu wike thaw??!???!!
#$tip: like bot? add a fake number to it. Just type a number (without sign)
#simp: call someone out for simping, @ them after the command
#ping <@445268344015290378> if bots down or you want something added and I'll see what I can do lol""")

async def createGithubIssue(postTitle, postBody, postAuthor):
    if postTitle == "" or postBody == "":
        return
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": postTitle,
        "body": f"{postBody}\n Reported by {postAuthor}.\n This issue was created automatically by Overseer, yell at Lyroth if its broken"
    }
    response = requests.post(GITHUB_API_URL, headers=headers, json=data)
    if response.status_code == 201:
        issue_url = response.json().get("html_url")
        print("Successfully created issue")
        return issue_url
    else:
        print(f"Failed to create issue: {response.content}")
        return None

bot.run(TOKEN)
