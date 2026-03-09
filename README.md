# visCOT: visualizing the tree representations of structurally stable incompressible flows in two dimensional multiply-connected domains

このプログラムは2次元多重連結領域内における構造安定な非圧縮流れの木表現の入力に対して，同一のトポロジーを表す2次元上の図を作図するものです．
想定されている入力は，Consで繋がれた木を同一の高さとして見た場合の，深さが3までの木です．

## Requirements
+ Python3 (>= 3.10)
+ matplotlib (>= 3.7)
+ numpy (>= 1.24)
+ scipy (>= 1.10)
+ PLY (>= 3.11)

## インストール

```
git clone https://github.com/yokoyama-lab/visCOT.git
cd visCOT
pip install -e . --break-system-packages
```

開発用の依存パッケージ（pytest, ruff, mypy）も合わせてインストールする場合:

```
pip install -e ".[dev]" --break-system-packages
```

## 実行例

COT木表現を標準入力から与えて可視化する:

```
echo "A0(a2(c+(l+,).c+(l+,),c-(l-,).c-(l-,)))" | viscot
```

ファイルに保存する場合:

```
echo "A0(a2(c+(l+,).c+(l+,),c-(l-,).c-(l-,)))" | viscot -o output.png
```

対話モードで起動する場合:

```
viscot -i
```

## テスト

```
make test
```

## Lint

```
make lint
```
