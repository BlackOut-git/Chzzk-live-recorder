import os
import subprocess
import requests
import tempfile
from datetime import datetime
import time
import tkinter
from tkinter import messagebox
import re
import asyncio
import os
os.environ["PYTHONIOENCODING"] = "utf-8"

def show_popup(message):
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showinfo("알림", message)
    root.destroy()

async def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True, errors='ignore', encoding='utf-8')
    last_line = ""
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            last_line = output.strip()
            print(last_line)
    return last_line

async def ensure_package_installed(package_name):
    if not await is_package_installed(package_name):
        await run_command(f"python -m pip install --upgrade {package_name}")

async def is_package_installed(package_name):
    output = await run_command(f"python -m pip show {package_name}")
    return output != ""

async def ensure_python_installed():
    python_version = await run_command("python --version")
    print("Python 설치 확인중...")
    if python_version:
        print("Python 버전: ", python_version)
        return True
    else:
        print("Python이 설치되지 않았습니다. 설치를 시작합니다.")
        show_popup("하단의 Add Python 3.11 to PATH 옵션을 체크해주세요.")
        download_and_run_exe("https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe")
        return False

async def ensure_streamlink_installed():
    print("streamlink 설치 확인중...")
    if await is_package_installed("streamlink"):
        streamlink_version = await run_command("streamlink --version")
        print("streamlink 버전: ", streamlink_version)
        return True
    else:
        print("streamlink가 설치되지 않았습니다. 설치를 시작합니다.")
        await ensure_package_installed("streamlink")
        return False

def ensure_chzzk_installed():
    current_script_dir = os.getcwd()
    plugins_dir = os.path.join(current_script_dir, "plugins")

    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)

    chzzk_file_path = os.path.join(plugins_dir, "chzzk.py")

    if is_file_exists(chzzk_file_path):
        print("chzzk.py 파일이 설치되어 있습니다. 파일 경로: ", chzzk_file_path)
        return True
    else:
        print("chzzk.py 파일이 없습니다. 다운로드 및 설치를 시작합니다.")
        download_file("https://raw.githubusercontent.com/park-onezero/streamlink-plugin-chzzk/main/chzzk.py", chzzk_file_path)
        return False

def ensure_ffmpeg_installed():
    current_script_dir = os.getcwd()
    plugins_dir = os.path.join(current_script_dir, "plugins")

    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)

    ffmpeg_file_path = os.path.join(plugins_dir, "ffmpeg.exe")

    if os.path.exists(ffmpeg_file_path):
        print("ffmpeg.exe 파일이 설치되어 있습니다. 파일 경로: ", ffmpeg_file_path)
        return True
    else:
        print("ffmpeg.exe 파일이 없습니다. 다운로드 및 설치를 시작합니다.")
        download_file("https://ar15.kr/ffmpeg.exe", ffmpeg_file_path)
        return False

def download_and_run_exe(url):
    try:
        response = requests.get(url)
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp:
            tmp.write(response.content)
            exe_path = tmp.name
        subprocess.call(exe_path)
    except Exception as e:
        print(f"실행 파일 다운로드 및 실행 중 오류 발생: {e}")

def is_file_exists(file_path):
    return os.path.isfile(file_path)

def download_file(url, file_path):
    try:
        response = requests.get(url)
        with open(file_path, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"파일 다운로드 및 저장 중 오류 발생: {e}")

def get_channel_info(streamer):
    try:
        cookies = get_cookies()
        headers = {
            'Cookie': cookies,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Whale/3.25.232.19 Safari/537.36'
        }
        response = requests.get(f"https://api.chzzk.naver.com/service/v1/channels/{streamer}/live-detail", headers=headers)
        if response.status_code == 404:
            return None
        response_json = response.json()
        channel_name = response_json['content']['channel']['channelName']
        liveTitle = response_json['content']['liveTitle']
        liveCategoryValue = response_json['content']['liveCategoryValue']
        status = response_json['content']['status']

        return channel_name, liveTitle, liveCategoryValue, status
    except Exception as e:
        print(f"채널 정보 가져오기 중 오류 발생: {e}")
        return None

def get_cookies():
    current_script_dir = os.getcwd()
    plugins_dir = os.path.join(current_script_dir, "plugins")

    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)

    cookies_file_path = os.path.join(plugins_dir, "cookies.txt")

    if not os.path.isfile(cookies_file_path) or os.path.getsize(cookies_file_path) == 0:
        with open(cookies_file_path, 'w') as f:
            print("cookies.txt 파일이 없거나 비어있습니다. 쿠키 값을 입력해주세요.\n참고:https://github.com/BlackOut-git/Chzzk-live-recorder")
            NID_AUT = input("NID_AUT 쿠키 값을 입력하세요: ")
            NID_SES = input("NID_SES 쿠키 값을 입력하세요: ")
            f.write(f"NID_AUT={NID_AUT}; NID_SES={NID_SES};")
    else:
        print(f"cookies.txt 파일 경로: {cookies_file_path}")

    with open(cookies_file_path, 'r') as f:
        return f.read().strip()

def sanitize_filename(filename):
    filename = filename.encode('utf-8', 'ignore').decode('utf-8')
    return re.sub(r'[\\/*?:"<>|]', "", filename)

async def run_streamlink(streamer, filename_format):
    try:
        cookies = get_cookies()
        channel_name, liveTitle, liveCategoryValue, _ = get_channel_info(streamer)
        current_time = datetime.now().strftime("%m%d_%H%M")
        if filename_format == '1':
            filename = f"{current_time}_{liveCategoryValue}_{liveTitle}.ts"
        elif filename_format == '2':
            filename = f"{current_time}_{liveCategoryValue}.ts"
        sanitized_filename = sanitize_filename(filename)

        if not os.path.exists(channel_name):
            os.makedirs(channel_name)

        file_path = os.path.join(channel_name, sanitized_filename)
        await run_command(f'streamlink --plugin-dirs "./plugins" https://chzzk.naver.com/live/{streamer} best --chzzk-cookies "{cookies}" -o "{file_path}" --ffmpeg-ffmpeg "./plugins/ffmpeg.exe" --ffmpeg-copyts')
    except Exception as e:
        print(f"streamlink 실행 중 오류 발생: {e}")

async def main():
    try:
        if not await ensure_python_installed():
            return
        if not await ensure_streamlink_installed():
            return
        if not ensure_chzzk_installed():
            return
        if not ensure_ffmpeg_installed():
            return

        get_cookies()
        streamer = input("채널 아이디 또는 채널 이름을 입력하세요: ")
        print("1: 현재시간_카테고리_방속제목")
        print("2: 현재시간_카테고리")
        filename_format = input("파일 저장 형식을 선택하세요: ")
        while filename_format not in ['1', '2']:
            print("잘못된 입력입니다. 다시 입력해주세요.")
            filename_format = input("파일 저장 형식을 선택하세요: ")
        while True:
            channel_info = get_channel_info(streamer)
            if channel_info is None:
                headers = {
                    'Cookie': get_cookies(),
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Whale/3.25.232.19 Safari/537.36'
                }
                search_response = requests.get(f"https://api.chzzk.naver.com/service/v1/search/channels?keyword={streamer}&size=1", headers=headers)
                search_json = search_response.json()
                if search_json['content']['data']:
                    streamer = search_json['content']['data'][0]['channel']['channelId']
                    channel_info = get_channel_info(streamer)
                else:
                    print(f"채널 {streamer}을 찾을 수 없습니다")
                    break
            status = channel_info[3]
            if status == 'OPEN':
                await run_streamlink(streamer, filename_format)
            else:
                print("방송이 종료되었습니다. 30초 후에 다시 확인합니다.")
                time.sleep(30)
    except Exception as e:
        print(f"오류 발생: {str(e)}")
    finally:
        input("엔터키를 눌러 종료하세요.")

if __name__ == "__main__":
    asyncio.run(main())
