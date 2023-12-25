import os
import subprocess
import requests
import tempfile
import sys
from datetime import datetime
import time
import tkinter
from tkinter import messagebox
import re

def show_popup(message):
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showinfo("알림", message)
    root.destroy()

def run_command(command, capture_output=True):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=capture_output)
        return result.stdout if capture_output else None
    except Exception as e:
        print(f"명령 실행 중 오류 발생: {e}")

def ensure_package_installed(package_name):
    if not is_package_installed(package_name):
        run_command(["python", "-m", "pip", "install", package_name])

def is_package_installed(package_name):
    output = run_command(["python", "-m", "pip", "show", package_name])
    return output is not None

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
        response = requests.get(f"https://api.chzzk.naver.com/service/v1/channels/{streamer}/live-detail")
        response_json = response.json()
        channel_name = response_json['content']['channel']['channelName']
        liveTitle = response_json['content']['liveTitle']
        liveCategoryValue = response_json['content']['liveCategoryValue']

        return channel_name, liveTitle, liveCategoryValue
    except Exception as e:
        print(f"채널 정보 가져오기 중 오류 발생: {e}")
        return None

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def run_streamlink(streamer):
    try:
        channel_name, liveTitle, liveCategoryValue = get_channel_info(streamer)
        current_time = datetime.now().strftime("%m%d_%H%M")
        filename = f"{current_time}_{liveCategoryValue}_{liveTitle}.ts"
        sanitized_filename = sanitize_filename(filename)

        if not os.path.exists(channel_name):
            os.makedirs(channel_name)

        file_path = os.path.join(channel_name, sanitized_filename)

        run_command(['streamlink', '--plugin-dirs', './plugins', f'https://chzzk.naver.com/live/{streamer}', 'best', '-o', file_path, '--ffmpeg-copyts'], capture_output=False)
    except Exception as e:
        print(f"streamlink 실행 중 오류 발생: {e}")

def main():
    try:
        python_version = run_command(["python", "--version"])
        print("Python 설치 확인중...")
        if python_version:
            print("Python 버전: ", python_version.decode('utf-8'))
            print("streamlink 설치 확인중...")
            if is_package_installed("streamlink"):
                streamlink_version = run_command(["streamlink", "--version"])
                print("streamlink 버전: ", streamlink_version.decode('utf-8'))

                current_file_dir = os.path.dirname(os.path.realpath(sys.executable))
                plugins_dir = os.path.join(current_file_dir, "plugins")

                if not os.path.exists(plugins_dir):
                    os.makedirs(plugins_dir)

                chzzk_file_path = os.path.join(plugins_dir, "chzzk.py")

                if is_file_exists(chzzk_file_path):
                    print("chzzk.py 파일이 설치되어 있습니다. 파일 경로: ", chzzk_file_path)
                    streamer = input("스트리머 아이디를 입력하세요: ")
                    while True:
                        channel_info = get_channel_info(streamer)
                        if channel_info is None:
                            print("생방송 정보를 가져오지 못했습니다. 30초 이후에 다시 시도합니다.")
                            time.sleep(30)
                            continue
                        else:
                            run_streamlink(streamer)
                else:
                    print("chzzk.py 파일이 없습니다. 다운로드 및 설치를 시작합니다.")
                    download_file("https://github.com/park-onezero/streamlink-plugin-chzzk/blob/main/chzzk.py", chzzk_file_path)

            else:
                print("streamlink가 설치되지 않았습니다. 설치를 시작합니다.")
                ensure_package_installed("streamlink")
                streamlink_version = run_command(["streamlink", "--version"])
                print("streamlink 버전: ", streamlink_version.decode('utf-8'))

        else:
            print("Python이 설치되지 않았습니다. 설치를 시작합니다.")
            show_popup("하단의 Add Python 3.11 to PATH 옵션을 체크해주세요.")
            download_and_run_exe("https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
    finally:
        input("아무 키나 눌러 종료하세요.")

if __name__ == "__main__":
    main()