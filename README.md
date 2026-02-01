윈도우 Powershell에서 실행할경우, 관리자 권한으로 다음을 실행해주세요.

```
Set-ExecutionPolicy RemoteSigned
```

해당 폴더에서
```
python -m venv .venv
```
venv 진입
```
/./.venv/Scripts/activate.ps1
```
필요한 패키지 설치
```
pip install -r ./requirements.txt
```
실행
```
python ./oscout.py
```
