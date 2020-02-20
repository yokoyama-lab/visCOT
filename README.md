# Visualization program of tree representation of structurally stable incompressible flow in two dimensional multiply-connected domain

このプログラムは2次元多重連結領域内における構造安定な非圧縮流れの木表現の入力に対して，同一のトポロジーを表す2次元上の図を作図するものです．
想定されている入力は，Consで繋がれた木を同一の高さとして見た場合の，深さが3までの木です．

## Requirements
+ Python3
+ Matplotlib
+ PLY

## Linux Ubuntuにてインストール例
+ 本プログラムをダウンロード
```
git clone https://github.com/yokoyama-lab/Visualization-program-of-flow.git
```

+ Python をインストール
```
sudo apt install python3
```

+ Matplotlib をインストール
```
cd Thesis_program
pip3 install Matplotlib
pip3 install numpy
pip3 install scipy
```

+ PLY をインストール
```
pip3 install PLY
```

## 実行例
プログラムを起動し，木表現を入力する．
```
python3 visualize.py
```

木表現は，例えば次のように入力する．
```
a0(cons(a2(cons(c+(l,n),cons(c+(l,n),n)),cons(c-(l,n),cons(c-(l,n),n))),n))
```

入力用の木表現が「test.txt」に用意されているので試してみてください．
