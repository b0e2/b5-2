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
mini-git> merge feature
mini-git> log
mini-git> log --sort-by=date
mini-git> log --sort-by=author
mini-git> path 00000002 00000003
mini-git> ancestors 00000002
mini-git> search login
mini-git> search "login feature"
mini-git> search --author=Alice
mini-git> diff "old notes.txt" "new notes.txt"
mini-git> quit
```

기본 `log`는 저장소의 모든 커밋을 부모가 자식보다 먼저 나오도록 출력합니다. 정렬 옵션은 날짜 또는 작성자 순서이며 동률에서는 기존 커밋 순서를 유지합니다. `path`는 부모-자식 연결을 양방향으로 보고 최단 경로를 찾습니다. 길이가 같으면 hash 경로 문자열의 사전순으로 선택합니다.

메시지 검색은 공백 단위 소문자 토큰의 역색인을 사용합니다. 공백이 있는 검색어는 연속된 토큰 구문으로 찾고, 작성자 검색은 이름이 정확히 일치해야 합니다. `init`을 다시 실행하면 현재 저장소 상태가 초기화됩니다.

`diff`는 로컬 UTF-8 텍스트 파일 두 개의 줄을 비교해 공통(` `), 삭제(`-`), 추가(`+`)를 표시합니다. `merge`는 현재 HEAD와 대상 브랜치 HEAD를 부모로 하는 새 커밋을 만듭니다. 둘 다 커밋이 있어야 하며 파일 내용이나 충돌을 병합하지는 않습니다.

커밋 ID는 세션 내 고유한 증가 번호의 16진수 표현이며 실제 Git의 콘텐츠 해시는 아닙니다. 파일 내용 추적, 디스크 저장, 네트워크 통신은 지원하지 않습니다. 프로그램 종료 시 저장된 커밋은 사라집니다.

## 테스트와 정렬 비교

```bash
python3 -m unittest discover -s tests
python3 benchmark_sort.py
```

정렬 비교는 고정 시드의 동일한 입력을 크기별로 만들어 각 알고리즘을 5회 측정한 평균 밀리초를 출력합니다. 기존 병합 정렬은 평균·최악 O(n log n), 삽입 정렬은 평균·최악 O(n²)이며 둘 다 같은 키의 원래 순서를 유지합니다. 실행 시간은 환경에 따라 달라집니다.
