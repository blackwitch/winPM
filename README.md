# winPM

windows 프로세스들의 관리에 도움을 줄 수 있는 프로젝트입니다.

## about winPM

winPM은 예기치 않은 에러로 프로세스가 다운될 경우 다시 시작하게 하거나 아예 일정 시간 별로 재시작 되도록 제어할 수 있습니다.

## 빌드하기

python이 설치되지 않은 시스템에서의 사용을 위해 pyinstaller(https://pypi.org/project/PyInstaller/) 사용을 권장합니다.

## 사용하기

config.json 파일을 만들어 그 안에 제어를 할 task를 정의해야 합니다. 

config 파일은 json 포멧으로 구성되며 아래와 내용을 설정할 수 있습니다.

[ task를 위한 설정 요소 ]

- name : task에 대한 설명을 정의할 수 있습니다. 실제 사용에는 영향을 미치지 않습니다.
- path : 제어하려는 프로세스의 실행 파일이 위치한 경로를 설정합니다. 
- file : 제어하려는 프로세스의 실행 파일명을 설정합니다.
- title : 프로세스 제어를 위해 파라미터로 사용될 명칭을 설정합니다.
- schedule : 프로세스 상태를 확인하는 시간 간격(cron, crontab format을 사용하세요.)과 상태 확인을 더 이상 하지 않을 시간(finish_datetime)을 지정합니다.
- buttons(option) : console 프로젝트가 아닌 경우 시작 혹은 종료 버튼을 제어할 필요가 있을 수 있습니다.
	- "START" : 프로세스를 가동 후 이 컬럼에 명시된 라벨의 버튼을 찾아 클릭합니다.
	- "STOP" : 프로세스 종료를 명령할 경우 종료 전 가동을 멈출 버튼을 눌러야 한다면 이 곳에 버튼의 라벨을 등록하세요.
- "QUIT" : 정상적인 종료를 위한 버튼이 있다면 이 곳에 버튼의 라벨을 등록하세요.
	- (* 각 버튼들은 명시되지 않았다면 무시하고 진행합니다.)
	- (* QUIT 버튼이 명시되지 않았다면 taskkill /f 를 이용해 프로세스를 종료시킵니다.)
- job : schedule-cron에 명시된 시간 간격마다 "sustenance"(프로세스를 감시하고 다운된 경우 자동으로 재가동 합니다.) 혹은 "restart"(프로세스를 강제로 종료 후 재가동 시킵니다.)합니다.

config.json의 샘플은 아래와 같습니다. 
```json
{ 
	# task는 필요한 만큼 정의 할 수 있습니다. 
	"task": [ { 
		"name": "샘플 A 프로세스", # task에 대한 설명입니다. 작업에 영향을 미치지 않습니다. 
		"path": "D:/sampleA", # 실행할 파일이 있는 path를 지정합니다. 
		"file": "hello.exe", # 실행할 파일명을 지정합니다. 
		"title": "hello_1", # task 관리 시 사용하는 명칭입니다. 16자를 넘지 않게 지정하세요. 
		"schedule": { 
			# cron은 체크할 주기를 지정하고 finish_datetime은 task의 종료일정을 지정하세요. (현재는 사용하지 않습니다.) 
			"cron": "* * * * *", 
			"finish_datetime": "2999-12-31" 
		}, 
		"buttons": { 
			"START": "START" # 시작 시 어떤 버튼을 눌러야 한다면 해당 버튼의 라벨을 지정하세요. 
		}, 
		"job": "sustenance" # 프로세스가 다운된 경우 재시작 합니다. 
	}, 
	{ 
		"name": "샘플 B 프로세스",
		"path": "E:/sample/sampleB", 
		"file": "hello2.exe", 
		"title": "hello_2", 
		"schedule": { 
			"cron": "0 0 * * *", 
			"finish_datetime": "2999-12-31" 
		}, 
		"buttons": { 
			"QUIT": "EXIT" # 종료 시 버튼을 눌러야 한다면 해당 버튼의 라벨을 지정하세요. 시작 시 눌러야할 버튼이 필요하다면 START를 같이 명시하세요. 
		}, 
		"job": "restart" # 지정된 시간에 프로세스를 재시작 합니다. 
	} 
]}
```

## 앞으로..

현재는 console 형태로 프로그램이 실행되지만 관리 편의를 위해 window service 로 수정할 예정입니다.


## License infomation

__winPM__ is distributed under the terms and conditions of the MIT license.
