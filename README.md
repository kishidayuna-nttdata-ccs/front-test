1. ソースを作成するディレクトリを用意し実行
python -m venv .venv

2. .venvディレクトリがあるディレクトリで実行（pythonの仮想環境設定）
source .venv/bin/activate

3. 必要なライブラリのインストール
pip install -r requirements.txt

4. flaskで実装したwebアプリの起動
gunicorn -w 1 -b 0.0.0.0:8000 app:app

etc. pythonの仮想環境設定を抜ける場合
deactivate
