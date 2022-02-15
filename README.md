# visCOT: visualizing the tree representations of structurally stable incompressible flows in two dimensional multiply-connected domains

このプログラムは2次元多重連結領域内における構造安定な非圧縮流れの木表現の入力に対して，同一のトポロジーを表す2次元上の図を作図するものです．
想定されている入力は，Consで繋がれた木を同一の高さとして見た場合の，深さが3までの木です．

## Requirements
+ Python3 (>= 3.8.5)
+ Matplotlib (>= 3.3.1)
+ numpy (>=1.19.1)
+ scipy (>=1.5.2)
+ PLY (>= 3.10)

## Linux Ubuntuにてインストール例
+ 本プログラムをダウンロード
```
git clone https://github.com/yokoyama-lab/Visualization-program-of-flow.git
```

+ Python をインストール
```
sudo apt install python3
```

+ Matplotlib, numpy, scipy, PLY をインストール
```
pip3 install Matplotlib
pip3 install numpy
pip3 install scipy
pip3 install PLY
```

## 実行例
プログラムを起動し，木表現を入力する．
```
echo "a0(a+(s+).a-(s-).a2(c+(s+,L-),L-))" | python3 visualize.py
```
