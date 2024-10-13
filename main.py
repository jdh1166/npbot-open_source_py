import shutil
import psutil
import discord
from discord.ext import commands, tasks
import sqlite3
import os
import aiohttp
import zipfile
import io
import random
import traceback
from queue import Queue
import subprocess
import asyncio
import requests
import json
import sys
import platform
from datetime import datetime
import yt_dlp
import logging
from dotenv import load_dotenv

intents = discord.Intents.all()
intents.messages = True

bot = commands.Bot(command_prefix='$', intents=intents)

#함수모으는곳
allowed_user_id = your_discord_id
webhook_url = 'your_server_webhook'

#.env파일 읽기

load_dotenv()

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

#음악재생함수
voice_channel = None
voice_client = None

# 시간단위 함수
def format_seconds(seconds):
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return int(days), int(hours), int(minutes), int(seconds)

@bot.event
async def on_error(event, *args, **kwargs):
    # 에러 로그 파일에 에러 기록
    with open('error.log', 'a', encoding='utf-8') as log_file:
        traceback.print_exc(file=log_file)

# SQLite 데이터베이스 연결
conn = sqlite3.connect('responses.db')
cursor = conn.cursor()

# 테이블 생성 (한 번만 실행)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        response TEXT NOT NULL,
        timestamp TEXT
    )
''')
conn.commit()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

        # 사용자 지정 상태 설정 (영화 보는 중 + 링크)
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Made By Fisher",
            url="https://www.youtube.com/@NP_FishermanV4"  # 여기에 링크를 넣어주세요
        )
    )

    channel_id = 971045839105572864  # 채팅 ID추가하기(시작했을때 메세지가 나올채널)
    channel = bot.get_channel(channel_id)
    
    if channel:
        await channel.send('bot is starting.')
    
    # jishaku 확장 로드
    await bot.wait_until_ready()
    await bot.load_extension('jishaku')
    
    # Jishaku 명령어의 정보 수정
    jsk_cog = bot.get_cog('Jishaku')
    if jsk_cog:
        jsk_cog.active_invocation_message = True  # 명령어 실행 메시지 활성화
        jsk_cog.active_interface_message = True  # 인터페이스 메시지 활성화
        jsk_cog.instance_check = True  # 버전 정보 메시지 활성화
        jsk_cog.retained_data_filter = lambda k, v: False  # 유지된 데이터 필터 비활성화


text_file_path = 'responses.txt'
# 백슬래시를 두 번 사용
text_file_directory = 'coding/npbot-raspi/newbot'

# Discord 봇 스레드 시작 함수
def start_bot(queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())
    queue.put("봇 종료")

@bot.command(name='cpu')
async def show_cpu_info(ctx):
    # 각 코어의 사용률을 가져옴
    cpu_percentages = psutil.cpu_percent(percpu=True)

    # 총 CPU 사용률을 가져옴
    total_cpu_percentage = psutil.cpu_percent()

    # 사용 가능한 메모리 정보를 가져옴
    memory_info = psutil.virtual_memory()

    # 라배에는 온도 측정 없음 (일단 보류)
    cpu_temp = 0

    # 시스템 정보를 가져옵니다.
    system_info = f"**System Information**\n"
    system_info += f"System: {platform.system()} {platform.version()}\n"
    system_info += f"Processor: {get_cpu_model()}\n"  # 수정된 부분
    system_info += f"Architecture: {platform.architecture()}\n"
    system_info += f"Machine: {platform.machine()}\n"

    # 메모리 정보를 가져와서 출력합니다.
    memory_info_str = f"**Memory Usage**\n"
    memory_info_str += f"Total: {format(memory_info.total, ',d')} bytes\n"
    memory_info_str += f"Available: {format(memory_info.available, ',d')} bytes\n"
    memory_info_str += f"Used: {format(memory_info.used, ',d')} bytes\n"
    memory_info_str += f"Percentage: {memory_info.percent}%\n"

    # 메시지를 만들어 보냅니다.
    message = "```"
    for core, usage in enumerate(cpu_percentages):
        message += f"Core {core}: Usage {usage}%\n"
    message += f"Total CPU Usage: {total_cpu_percentage}%\n"
    message += f"CPU Temperature: {cpu_temp}°C\n"
    message += f"\n{system_info}\n{memory_info_str}"
    message += "```"

    await ctx.send(message)

def get_cpu_model():
    # /proc/cpuinfo (only linux)
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line.startswith('model name'):
                return line.split(':')[1].strip()

@bot.command(name='console')
async def show_recent_error(ctx):
    if ctx.author.id == allowed_user_id:
        try:
            # 최근 콘솔에서 발생한 에러 로그 가져오기
            with open('error.log', 'r', encoding='utf-8') as log_file:
                error_logs = log_file.readlines()

            # 최근 콘솔에서 발생한 에러 로그를 보여줌
            if error_logs:
                await ctx.send(f'recent console error :\n```\n{" ".join(error_logs)}\n```')
            else:
                await ctx.send('none console error.')
        except Exception as e:
            # 예외가 발생한 경우 traceback 출력
            traceback_str = traceback.format_exc()
            await ctx.send(f' recent error traceback :\n```\n{traceback_str}\n```')
    else:
        await ctx.send('none permission.')

@bot.command(name='낚시꾼')
async def generate_channel_link(ctx):
    # 특정 유튜브 채널의 링크
    channel_link = 'https://www.youtube.com/channel/UCRIGdAzcgtixGksw0tJ6zDA'

    await ctx.send(f'구독 안하면 내얼굴 {channel_link}')

@bot.command(name='네르')
async def generate_channel_link(ctx):
    # 특정 유튜브 채널의 링크
    channel_link = 'https://www.youtube.com/@NP_NER'

    await ctx.send(f'{channel_link}')


#컴퓨터 정보 불러오기
@bot.command(name='os정보')
async def get_os_info(ctx):
    system_info = platform.system()
    node_info = platform.node()
    release_info = platform.release()

    # CPU 정보 가져오기
    cpu_percent = psutil.cpu_percent(interval=1)

    # 메모리 정보 가져오기
    memory_info = psutil.virtual_memory()
    memory_percent = memory_info.percent

    # 디스크 정보 가져오기
    disk_info = psutil.disk_usage('/')
    total_space = shutil.disk_usage('/').total
    free_space = disk_info.free

    response = (
        f'os: {system_info}\n'
        f'host name: {node_info}\n'
        f'os relese: {release_info}\n'
        f'CPU usage: {cpu_percent}%\n'
        f'memory usage: {memory_percent}%\n'
        f'전체 저장 공간: {total_space / (1024 ** 3):.2f} GB\n'
        f'남은 저장 공간: {free_space / (1024 ** 3):.2f} GB'
    )

    await ctx.send(response)

@bot.command(name='join')
async def join(ctx):
    global voice_channel

    # 이미 봇이 음성 채널에 있는 경우 무시
    if ctx.voice_client is not None:
        return

    voice_channel = ctx.author.voice.channel
    await voice_channel.connect()
    await ctx.send(f'join the voice chennel.')

@bot.command(name='play', aliases=['플레이'])
async def play(ctx, url):
    # 봇이 음성 채널에 참여하지 않은 경우
    if not ctx.voice_client:
        channel = ctx.author.voice.channel
        await channel.connect()

    # 음성 채널에 봇이 참여한 후 노래를 재생
    voice_channel = ctx.voice_client

    with yt_dlp.YoutubeDL(bot.ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print(f"Selected format: {info['formats'][0]}")
        url2 = info['formats'][0]['url']
        voice_channel.play(discord.FFmpegPCMAudio(url2, executable='ffmpeg', options='-vn -ar 48000 -ac 2'), after=lambda e: print('done', e))

    await ctx.send(f'playing music: {url}')


@bot.command(name='reboot')
async def restart_bot(ctx):
    if ctx.author.id == allowed_user_id:
        await ctx.send('reboot.....')

        # 현재 실행 중인 봇 프로세스 종료
        script_path = '/home/desktop/coding/npbot-raspi/newbot/bot2.py'
        subprocess.Popen([sys.executable, script_path])

        # 봇 로그아웃
        await bot.close()
    else:
        await ctx.send('you need permission.')

@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)  # 응답 지연 시간을 밀리초로 변환
    await ctx.send(f'ping: {latency}ms')

@bot.command(name='save')
async def save_response(ctx, *, response):
    if ctx.author.id == allowed_user_id:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('INSERT INTO responses (response, timestamp) VALUES (?, ?)', (response, current_time))
        conn.commit()

        cursor.execute('SELECT last_insert_rowid()')
        result = cursor.fetchone()

        if result:
            response_number = result[0]

            if not os.path.exists(text_file_directory):
                os.makedirs(text_file_directory)

            with open(os.path.join(text_file_directory, text_file_path), 'a', encoding='utf-8') as text_file:
                text_file.write(f'{response_number}: {response} (Timestamp: {current_time})\n')

            await ctx.send(f'saved ({response_number})')
        else:
            await ctx.send('save falied.')
    else:
        await ctx.send('none permisson.')

@bot.command(name='db')
async def retrieve_response(ctx, index: int):
    if ctx.author.id == allowed_user_id:
        # 인덱스에 해당하는 답변과 시간을 조회
        cursor.execute('SELECT response, timestamp FROM responses WHERE id = ?', (index,))
        result = cursor.fetchone()

        if result:
            await ctx.send(f'info {index}: {result[0]} (Timestamp: {result[1]})')
        else:
            await ctx.send('none.')
    else:
        await ctx.send('none permission.')

@bot.command(name='delete_db')
async def delete_response(ctx, index: int):
    if ctx.author.id == allowed_user_id:
        # 인덱스에 해당하는 답변을 삭제
        cursor.execute('DELETE FROM responses WHERE id = ?', (index,))
        conn.commit()
        await ctx.send(f'{index}is deleted.')
    else:
        await ctx.send('none permission.')

@bot.command(name='저장파일')
async def save_file(ctx):
    if ctx.author.id == allowed_user_id:
        await ctx.send('put the file in 10sec.')

        def check(message):
            return message.author == ctx.author and message.attachments

        try:
            message = await bot.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            print("Timeout error occurred")  # 디버그 출력 추가
            await ctx.send('timeout please try again.')
            return
        except Exception as e:
            print(f"An error occurred: {e}")  # 디버그 출력 추가
            await ctx.send(f'An error occurred: {e}')
            return

        # 파일을 저장할 디렉토리 확인 및 생성
        if not os.path.exists(text_file_directory):
            os.makedirs(text_file_directory)

        # 첨부 파일 저장
        attachment = message.attachments[0]
        file_id = random.randint(1000, 9999)  # 1000부터 9999까지의 임의의 숫자
        file_path = os.path.join(text_file_directory, f'file_{file_id}{os.path.splitext(attachment.filename)[1]}')  # 파일 경로를 ID에 따라 지정

        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                data = await resp.read()
                with open(file_path, 'wb') as f:
                    f.write(data)

        # 파일의 ID와 생성 시간을 말하기
        creation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await ctx.send(f'Succeed save file. ID: {file_id}, made time: {creation_time}')
    else:
        await ctx.send('you need permission.')

@bot.command(name='file_id')
async def send_file(ctx, file_id: int):
    if ctx.author.id == allowed_user_id:
        # 파일의 경로를 지정
        file_path_pattern = f'file_{file_id}'
        matching_files = [file for file in os.listdir(text_file_directory) if file.startswith(file_path_pattern)]

        if matching_files:
            # 찾은 파일들 중에서 일치하는 파일이 있는지 확인
            matching_file = next((file for file in matching_files), None)

            if matching_file:
                file_path = os.path.join(text_file_directory, matching_file)

                # zip 파일 생성
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                    zipf.write(file_path, matching_file)

                # zip 파일 전송
                zip_buffer.seek(0)
                await ctx.send(file=discord.File(zip_buffer, filename=f'file_{file_id}.zip'))
            else:
                await ctx.send(f'file_{file_id}로 시작하는 파일이 존재하지 않습니다.')
        else:
            await ctx.send('not found.')
    else:
        await ctx.send('none permission.')

@bot.command(name='file_list')
async def file_list(ctx):
    if ctx.author.id == allowed_user_id:
        files = os.listdir(text_file_directory)
        if files:
            file_info = []
            for file in files:
                if file.startswith('file_'):
                    file_path = os.path.join(text_file_directory, file)
                    creation_time = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    file_info.append(f'{file}: {creation_time}')

            if file_info:
                await ctx.send('\n'.join(file_info))
            else:
                await ctx.send('no saved file.')
        else:
            await ctx.send('none saved file.')
    else:
        await ctx.send('none permission')

@bot.command(name='delete_file')
async def delete_file(ctx, file_id: int):
    if ctx.author.id == allowed_user_id:
        # 삭제할 파일의 경로를 지정
        file_path_pattern = f'file_{file_id}'
        matching_files = [file for file in os.listdir(text_file_directory) if file.startswith(file_path_pattern)]

        if matching_files:
            # 찾은 파일들 중에서 일치하는 파일이 있는지 확인
            matching_file = next((file for file in matching_files), None)

            if matching_file:
                file_path = os.path.join(text_file_directory, matching_file)

                # 파일 삭제
                os.remove(file_path)

                await ctx.send(f'{matching_file} 파일이 삭제되었습니다.')
            else:
                await ctx.send(f'{file_path_pattern}로 시작하는 파일이 존재하지 않습니다.')
        else:
            await ctx.send('삭제할 파일이 없습니다.')
    else:
        await ctx.send('죄송합니다. 권한이 없습니다.')

@bot.command(name='종료')
async def shutdown(ctx):
    if ctx.author.id == allowed_user_id:
        await ctx.send('봇을 종료합니다.')

        # discord.py 버전에 따라 메서드 호출 방식 변경
        if discord.__version__.startswith('1.'):
            await bot.logout()
        else:
            await bot.close()
    else:
        await ctx.send('죄송합니다. 권한이 없습니다.')

#에러로깅
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        # 에러 메시지 가져오기
        error_message = str(error)

        # 트레이스백 가져오기
        traceback_text = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

        # 메시지 길이가 2000자를 초과하는 경우 최대 2000자까지만 전송  
        if len(error_message) + len(traceback_text) > 2000:
            remaining_chars = 2000 - len(error_message)

            # 오류코드 잘린거
            trimmed_traceback = traceback_text[:remaining_chars]

            # 메시지 전송
            await ctx.send(f'{error_message}\n```{trimmed_traceback}```')

            # 나머지 부분들 계속 전송
            for i in range(remaining_chars, len(traceback_text), 2000):
                await ctx.send(f'```{traceback_text[i:i+2000]}```')
        else:
            # 메시지 길이가 2000자 이하인 경우 전체 메시지를 전송
            await ctx.send(f'{error_message}\n```{traceback_text}```')


@bot.command(name='공지')
async def send_announcement(ctx, *, content):
    if ctx.author.id == allowed_user_id:
        # 웹훅으로 보낼 페이로드 작성
        payload = {
            'content': f'**공지:** {content}',  # 원하는 형식으로 메시지 포맷팅
            'username': 'NP',  # 웹훅의 사용자 이름을 'NP'로 설정
            'avatar_url': str(bot.user.avatar.url)  # 웹훅의 아바타를 봇의 아바타로 설정
        }
        headers = {
            'Content-Type': 'application/json'
        }

        # 웹훅을 사용하여 메시지 전송
        response = requests.post(webhook_url, json=payload, headers=headers)

        if response.status_code == 204:
            await ctx.send('공지가 성공적으로 전송되었습니다.')
        else:
            await ctx.send('공지 전송에 실패했습니다.')
    else:
        await ctx.send('죄송합니다. 권한이 없습니다.')



#봇실행
bot.run('봇토큰')
