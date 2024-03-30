<a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FBlackOut-git%2FChzzk-live-recorder&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false"/></a>

# Chzzk Live Recorder
Main Idea: https://github.com/park-onezero/streamlink-plugin-chzzk  
Python 설치 필요 https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe  

기본 30초인 딜레이를 변경하려면 **line 208: time.sleep(30)** 의 30을 원하는 값으로 변경하면 됩니다.  

채널 ID 또는 채널 이름에는 URL의 `a74f103809ed746b0d867b114ceb33ab`와 같은 고유 ID 혹은 채널 이름인 `몽실s`를 입력해야됩니다.  

Python, Streamlink, FFmpeg, Streamlink Plugin Chzzk.py를 이용한 자동 녹화 시스템입니다.  
실행에 필요한 모든 파일이 설치되어있는지 확인하고 아니라면 설치하는 기능이 포함되어있고  
채널 ID 또는 채널 이름를 입력받아 방송이 켜져있는지 30초마다 확인하여 자동으로 녹화를 진행합니다.  

## 쿠키값 확인 방법
1. 네이버 치지직에 로그인합니다 https://chzzk.naver.com/
2. F12 -> 상단 Application -> 좌측 Cookies -> NID_AUT , NID_SES 두개의 값이 필요합니다
![쿠키](https://github.com/BlackOut-git/Chzzk-live-recorder/assets/94197378/461e7d80-4391-4353-a27a-708b0b199205)
