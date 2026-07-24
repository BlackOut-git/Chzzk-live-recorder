# chzzk-live-recorder

치지직 방송을 자동으로 녹화하는 Windows용 도구다. 지정한 채널의 방송이 켜지면 Streamlink와 FFmpeg로 녹화하며, 실행에 필요한 네이버 로그인 쿠키는 첫 실행 때 입력받는다.

## 기능

- 채널 온에어 감지와 자동 녹화, 방송이 다시 켜지면 녹화 재개
- 채널 ID와 채널명 모두 입력 가능, 채널명은 검색 API로 ID를 자동 해석
- 파일명 형식 선택: 녹화시각_카테고리_방송제목 또는 녹화시각_카테고리
- 녹화 파일을 채널명 폴더에 분류 저장
- Streamlink, FFmpeg, 치지직 플러그인이 없으면 자동 설치

## 동작 방식

치지직 `live-detail` API로 방송 상태를 조회해 `OPEN`이면 녹화를 시작하고, 아니면 30초 후 다시 확인한다. 이 폴링 간격 때문에 방송 시작 직후 일부 구간은 누락될 수 있다. Streamlink가 치지직 플러그인으로 최고 화질 스트림을 받아 로그인 쿠키와 함께 FFmpeg를 거쳐 `.ts` 파일로 기록한다.

## 실행

```
pip install -r requirements.txt
python Chzzk-live-recorder.py
```

실행하면 네이버 로그인 쿠키 `NID_AUT`, `NID_SES` 값과 채널, 파일명 형식을 차례로 물어본다. 쿠키는 `plugins/cookies.txt`에 저장되어 다음 실행부터는 다시 입력하지 않는다. FFmpeg는 `ffmpeg.exe`를 내려받아 사용하므로 Windows에서 실행해야 한다.
