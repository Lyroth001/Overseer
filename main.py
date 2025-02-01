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
BAN_CHANNEL_ID = int(os.getenv("BAN_CHANNEL_ID"))
DISCUSSION_CHANNEL_ID = int(os.getenv("DISCUSSION_CHANNEL_ID"))
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
adminDiscussion = None

# Runs when Bot Succesfully Connects
@bot.event
async def on_ready():
    global adminDiscussion
    print(f'{bot.user} succesfully logged in!')
    adminDiscussion = await bot.get_channel(DISCUSSION_CHANNEL_ID)

# sends messages when detecting certain words
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)
@bot.event
async def on_thread_create(thread):
    global adminDiscussion
    if thread.channel.id == BUG_REPORTS_CHANNEL_ID:
        issueUrl = await createGithubIssue(thread)
        if issueUrl is not None:
            await thread.send(f"Created issue on GitHub: {issueUrl}")
    elif thread.channel.id == BAN_CHANNEL_ID:
        await adminDiscussion.create_thread(name=f"{thread.name} appeal discussion", message = f"Related ban appeal: {thread.jump_url}.\n This thread was created automatically by Overseer, yell at Lyroth if its broken")

async def createGithubIssue(thread):
    if thread.name == "" or thread.starter_message.content == "":
        return
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": thread.name,
        "body": f"{thread.starter_message.content}\n Reported by {thread.starter_message.author}.\n [Linked discord discussion]({thread.jump_url}).\n This issue was created automatically by Overseer, yell at Lyroth if its broken"
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
