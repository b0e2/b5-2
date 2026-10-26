# Mini Git

커밋 메타데이터를 메모리에 보관하고 브랜치, 그래프 탐색, 검색, 로그 정렬을 다루는 CLI입니다. 실제 Git처럼 파일 이력을 저장하는 도구는 아니며, Python 3.9 이상에서 실행합니다.

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

위 흐름에서는 첫 커밋이 `00000001`, `feature`의 커밋이 `00000002`, `main`의 다음 커밋이 `00000003`입니다. `merge feature`는 두 브랜치의 HEAD를 부모로 하는 `00000004`를 만듭니다. `diff` 예시를 실행하려면 이름에 맞는 로컬 UTF-8 텍스트 파일 두 개가 있어야 합니다.

## 명령 동작

- `init <user_name>`은 `main` 브랜치로 시작합니다. `branch <name>`은 현재 HEAD를 복사하고, `switch <name>`은 브랜치를 바꾸며, `commit <message>`는 현재 브랜치에 새 커밋을 추가합니다.
- `log`는 모든 커밋을 부모부터 출력합니다. `--sort-by=date|author`는 날짜·작성자순으로 정렬하며, 동률이면 기존 순서를 유지합니다.
- `path <hash> <hash>`는 부모-자식 연결을 양방향으로 탐색해 최단 경로를 찾습니다. 동률이면 hash 경로의 사전순으로 고릅니다. `ancestors <hash>`는 해당 커밋의 모든 조상을 찾습니다.
- `search <keyword>`는 메시지의 공백 단위 소문자 토큰을 역색인으로 찾습니다. 따옴표로 감싼 여러 단어는 연속된 구문을 찾고, `search --author=<name>`은 작성자 이름이 정확히 일치하는 커밋을 찾습니다.
- `diff <file1> <file2>`는 공통(` `), 삭제(`-`), 추가(`+`) 줄을 표시합니다. `merge <branch_name>`은 커밋의 부모 관계만 합치며 파일 내용이나 충돌을 병합하지 않습니다.

`init`을 다시 실행하면 저장소 상태가 초기화됩니다. 커밋 ID는 세션 내 고유한 증가 번호의 16진수 표현으로, 실제 Git의 콘텐츠 해시는 아닙니다. 디스크 저장과 네트워크 통신은 지원하지 않으며 프로그램을 종료하면 커밋도 사라집니다. `exit` 또는 `quit`로 종료할 수 있습니다.

## 구조

- `main.py`: 실행 진입점
- `mini_git/cli`: REPL과 명령 파싱·검증·출력
- `mini_git/core`: 커밋 모델, 저장소 상태, 검색 인덱스
- `mini_git/algorithms`: 그래프 탐색, 정렬, LCS 줄 비교
- `benchmarks`: 정렬 성능 비교
- `tests`: 기능별 단위 테스트와 CLI 통합 테스트

`mini_git/__init__.py`는 `Commit`, `Repository`, `MiniGitError`, 정렬 함수 등 기존 공개 import를 유지합니다.

## 테스트와 정렬 비교

```bash
python3 -m unittest discover -s tests
python3 -m benchmarks.sort_benchmark
```

정렬 비교는 고정 시드의 동일한 입력을 크기별로 만들어 각 알고리즘을 5회 측정한 평균 밀리초를 출력합니다. 병합 정렬은 평균·최악 O(n log n), 삽입 정렬은 평균·최악 O(n²)이며 둘 다 같은 키의 원래 순서를 유지합니다. 실행 시간은 환경에 따라 달라집니다.
