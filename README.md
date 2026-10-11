# Mini Git

커밋 메타데이터를 메모리에 보관하고 브랜치, 그래프 탐색, 역색인 검색, 로그 정렬을 제공하는 CLI입니다. Python 3.10 이상이 필요합니다.

## 실행

```bash
python3 main.py
```

`mini-git>` 프롬프트에서 명령을 입력합니다. 명령어는 대소문자를 구분하지 않으며, 공백을 포함하는 인자는 따옴표로 감쌉니다.

```text
mini-git> init "Alice"
mini-git> commit "Initial commit"
mini-git> branch feature
mini-git> switch feature
mini-git> commit "Add login feature"
mini-git> switch main
mini-git> commit "Add payment feature"
mini-git> log
mini-git> log --sort-by=date
mini-git> log --sort-by=author
mini-git> path 00000002 00000003
mini-git> ancestors 00000002
mini-git> search login
mini-git> search "login feature"
mini-git> search --author=Alice
mini-git> quit
```

기본 `log`는 저장소의 모든 커밋을 부모가 자식보다 먼저 나오도록 출력합니다. 정렬 옵션은 날짜 또는 작성자 순서이며 동률에서는 기존 커밋 순서를 유지합니다. `path`는 부모-자식 연결을 양방향으로 보고 최단 경로를 찾습니다. 길이가 같으면 hash 경로 문자열의 사전순으로 선택합니다.

메시지 검색은 공백 단위 소문자 토큰의 역색인을 사용합니다. 공백이 있는 검색어는 연속된 토큰 구문으로 찾고, 작성자 검색은 이름이 정확히 일치해야 합니다. `init`을 다시 실행하면 현재 저장소 상태가 초기화됩니다.

커밋 ID는 세션 내 고유한 증가 번호의 16진수 표현이며 실제 Git의 콘텐츠 해시는 아닙니다. 파일 내용 추적, 디스크 저장, 네트워크 통신은 지원하지 않습니다. 프로그램 종료 시 저장된 커밋은 사라집니다.

## 테스트

```bash
python3 -m unittest discover -s tests
```
