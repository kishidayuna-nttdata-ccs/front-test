from flask import Flask, request, redirect, url_for, session, render_template, jsonify
from dotenv import load_dotenv
from auth import check_credentials
from azure_agent import ask_azure_agent
import requests

load_dotenv()
app = Flask(__name__)
app.secret_key = "your_secret_key"

import certifi
print(certifi.where())

# /prompt: ユーザーのプロンプトをAzure Agentに投げて回答を返す
@app.route("/prompt", methods=["POST"])
def prompt():
    if "username" not in session:
        return redirect(url_for("login"))
    data = request.get_json()
    user_prompt = data.get("prompt", "")
    if not user_prompt:
        return jsonify({"answer": "プロンプトが空です。"})
    try:
        answer = ask_azure_agent(user_prompt)
    except Exception as e:
        answer = f"エージェント呼び出し時にエラー: {str(e)}"
    return jsonify({"answer": answer})

# GET: ログイン画面表示, POST: ログイン処理
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        if check_credentials(username, password):
            session["username"] = username
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "IDまたはパスワードが正しくありません。"}), 401
    # GETまたは認証失敗時はlogin.htmlを表示
    return render_template("login.html", error=error)

@app.route("/home")
def home():
    if "username" in session:
        return render_template("home.html", username=session["username"])
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)