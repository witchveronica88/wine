# Wine

마신 와인을 기록하는 개인 와인 노트입니다. → https://witchveronica88.github.io/wine/

## 구성

- `data/wines.json`: 와인 기록 전체예요. 모든 기기가 이 파일을 함께 봅니다.
- `photos/`: 와인 병 사진(`NNN.webp`)과 목록용 작은 사진(`NNN-thumb.webp`)
- `data/notes.json`: 와인 노트(품종·산지·기초 개념) 목록
- `index.html`: 앱 화면

## 와인 추가하기

Claude에게 사진과 와인 정보를 주고 "와인 추가해줘"라고 하면 됩니다. 순서는 `CLAUDE.md`에 정리해 두었어요.
`data/wines.json`에 추가된 와인은 모든 기기에 자동으로 나타납니다.

앱의 "기록 추가" 버튼으로 저장한 기록은 **그 기기의 브라우저에만** 저장돼요. 목록에 "이 기기에만 저장" 표시가 붙습니다.
다른 기기에서도 보려면 Claude에게 저장소에 추가해 달라고 하세요.
