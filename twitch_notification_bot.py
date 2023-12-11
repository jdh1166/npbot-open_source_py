import discord
from discord.ext import commands
import requests

# Discord 봇 토큰
TOKEN = 'YOUR_DISCORD_TOKEN'

# Twitch API 정보
CLIENT_ID = 'YOUR_TWITCH_CLIENT_ID'
CHANNEL_NAMES = ['TARGET_TWITCH_CHANNEL1', 'TARGET_TWITCH_CHANNEL2', 'TARGET_TWITCH_CHANNEL3',
                 'TARGET_TWITCH_CHANNEL4', 'TARGET_TWITCH_CHANNEL5', 'TARGET_TWITCH_CHANNEL6']

# 디스코드 봇 생성
bot = commands.Bot(command_prefix='!')

# 봇이 준비되었을 때 동작할 이벤트
@bot.event
async def on_ready():
    print(f'봇이 다음 이름으로 로그인합니다: {bot.user.name}')
    print(f'봇의 ID: {bot.user.id}')

# 트위치에서 방송 시작 알림 체크하는 함수
async def check_stream_status():
    for channel_name in CHANNEL_NAMES:
        url = f'https://api.twitch.tv/helix/streams?user_login={channel_name}'
        headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': 'Bearer YOUR_TWITCH_ACCESS_TOKEN'  # Twitch API Access Token을 입력해야 합니다.
        }
        response = requests.get(url, headers=headers)
        data = response.json()

        if 'data' in data and len(data['data']) > 0:
            # 방송이 시작되었을 경우
            stream_title = data['data'][0]['title']
            stream_url = f'https://www.twitch.tv/{channel_name}'
            channel = bot.get_channel(YOUR_DISCORD_CHANNEL_ID)  # 알림을 보낼 디스코드 채널 ID 입력
            await channel.send(f'{channel_name} 님이 방송을 시작했습니다!

{stream_title}
{stream_url}')

# 주기적으로 트위치 방송 상태 체크
@bot.event
async def on_ready():
    while True:
        await check_stream_status()
        await asyncio.sleep(60)  # 60초마다 체크

# 봇 실행
bot.run(TOKEN)