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
import sys

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
        headers = {
            'Cookie': 'NID_AUT=d3oAOabNESBfo+S+KfE08uY8fcnrKv2pnILAH6TYczERYnJiB44ZrXF4+ohMaRJO; NID_SES=AAABm1PTAAzAsSjSqu29jQ/3MQKlVFI7oLDJtIjfcNpAkSy2hpi5aZ74Kj/LhI9ClyLQjPEmETAhZZmNMwbYSgorGyFJn3IwvdL6iEPD8GbD7ZT7fc/ywkPgdyZyZhCBXLuLmUL0o15YLNOyEf1UvPwWhq147dP5JXs6J1dDiD6ohmoKoZEn3dlpvx7jkgSb0Mvp/tayd7md6pPCaKIghW6FusI7m/WlprXDo7oBHGLAabukfQKa/t+9V4bUa5E1vp9NkY8dufuXc0ObDsC9ZK52DEGpOCrWAawoZdq56peYmaquqI4mxTl2VVbySjveA70DdX7nKsyz31SNHhYkdON4py53WNX5o2NtT0L2a4oz4ENvP7NDVD5/9mPE/Shkg079cTUEdCqOwM1+BJAFJZb0RWHTkk+qyRki5b681w9iULLY5MVJt9yLkEkv1lBICFTnPCwOMRbJbK62iBWSqaN0uAkBCHihmbxF3pbsgNf4eqVldEFeixZdIkc1bmrJ8YI+Q5aRhy+BIlu6L9qvZaoQ+2WPNJj2Oca6Dvc8Ok94C4fB',
            }
        response = requests.get(f"https://api.chzzk.naver.com/service/v1/channels/{streamer}/live-detail", headers=headers)
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
    cookies_file_path = os.path.join(os.getcwd(), "cookies.txt")
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
        await run_command(f'streamlink --ffmpeg-copyts --plugin-dirs "./plugins" https://chzzk.naver.com/live/{streamer} best --chzzk-cookies "{cookies}" -o "{file_path}"')
    except Exception as e:
        print(f"streamlink 실행 중 오류 발생: {e}")

async def main():
    try:
        python_version = await run_command("python --version")
        print("Python 설치 확인중...")
        if python_version:
            print("Python 버전: ", python_version)
            print("streamlink 설치 확인중...")
            if await is_package_installed("streamlink"):
                streamlink_version = await run_command("streamlink --version")
                print("streamlink 버전: ", streamlink_version)

                current_script_dir = os.getcwd()
                plugins_dir = os.path.join(current_script_dir, "plugins")

                if not os.path.exists(plugins_dir):
                    os.makedirs(plugins_dir)

                chzzk_file_path = os.path.join(plugins_dir, "chzzk.py")

                if is_file_exists(chzzk_file_path):
                    print("chzzk.py 파일이 설치되어 있습니다. 파일 경로: ", chzzk_file_path)
                    get_cookies()
                    streamer = input("스트리머 아이디를 입력하세요: ")
                    print("1: 현재시간_카테고리_방속제목")
                    print("2: 현재시간_카테고리")
                    filename_format = input("파일 저장 형식을 선택하세요: ")
                    while filename_format not in ['1', '2']:
                        print("잘못된 입력입니다. 다시 입력해주세요.")
                        filename_format = input("파일 저장 형식을 선택하세요: ")
                    while True:
                        channel_info = get_channel_info(streamer)
                        if channel_info is None:
                            print(f"채널 {streamer}이(가) 존재하지 않습니다.")
                            break
                        status = get_channel_info(streamer)[3]
                        if status == 'OPEN':
                            await run_streamlink(streamer, filename_format)
                        else:
                            print("방송이 종료되었습니다. 30초 후에 다시 확인합니다.")
                            time.sleep(30)
                else:
                    print("chzzk.py 파일이 없습니다. 다운로드 및 설치를 시작합니다.")
                    download_file("https://raw.githubusercontent.com/park-onezero/streamlink-plugin-chzzk/main/chzzk.py", chzzk_file_path)

            else:
                print("streamlink가 설치되지 않았습니다. 설치를 시작합니다.")
                await ensure_package_installed("streamlink")

        else:
            print("Python이 설치되지 않았습니다. 설치를 시작합니다.")
            show_popup("하단의 Add Python 3.11 to PATH 옵션을 체크해주세요.")
            download_and_run_exe("https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
    finally:
        input("엔터키를 눌러 종료하세요.")

if __name__ == "__main__":
    asyncio.run(main())