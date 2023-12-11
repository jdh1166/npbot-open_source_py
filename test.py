import discord
from discord.ext import commands

# 봇의 접두사(prefix) 설정
prefix = "!"

# Intents 설정
intents = discord.Intents.all()

# 봇 생성 및 Intents 적용
bot = commands.Bot(command_prefix=prefix, intents=intents)

# 봇이 준비되었을 때 동작할 이벤트
@bot.event
async def on_ready():
    print(f'봇이 다음 이름으로 로그인합니다: {bot.user.name}')
    print(f'봇의 ID: {bot.user.id}')

# 메시지가 도착했을 때 동작할 이벤트
@bot.event
async def on_message(message):
    # 봇이 보낸 메시지는 무시
    if message.author.bot:
        return

    # 메시지 작성자가 봇의 접두사로 시작하는 명령어를 사용한 경우 동작
    if message.content.startswith(prefix):
        # 명령어 제거
        command = message.content[len(prefix):]

        # 여기에 명령어에 따른 동작을 추가해주세요.

        # 예시: "hello" 명령어에 대한 동작
        if command == "hello":
            await message.channel.send("Hello, World!")

# 봇 실행
bot.run("YOUR_BOT_TOKEN")