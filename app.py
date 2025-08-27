from flask import Flask, render_template_string, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "uhsdfhwfesd"

# --- データベース初期化 ---
def init_db():
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    song_id TEXT,
                    title TEXT,
                    composer TEXT,
                    genre TEXT,
                    number TEXT,
                    notes TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# --- HTMLテンプレート ---
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ログイン</title>
    <style>
        body { background-color: #add8e6; font-family: Arial; text-align:center; padding-top:100px; }
        input { padding:8px; margin:5px; width:200px; }
        button { padding:8px 15px; }
    </style>
</head>
<body>
    <h1>ログイン</h1>
    {% if error %}
        <p style="color:red;">{{ error }}</p>
    {% endif %}
    <form method="POST">
        <input type="password" name="password" placeholder="パスワード" required>
        <button type="submit">ログイン</button>
    </form>
</body>
</html>
"""

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>楽譜管理アプリ</title>
    <style>
        body { background-color: #add8e6; font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; display: inline-block; }
        .logout { float: right; margin-top: 20px; }
        form { margin-bottom: 20px; background: white; padding: 15px; border-radius: 10px; }
        label { display: block; margin-top: 10px; }
        input, textarea { width: 100%; padding: 5px; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; background: white; }
        th, td { border: 1px solid #aaa; padding: 8px; text-align: left; }
        th { background: #eee; }
        .delete-btn { color: white; background: red; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer; }
        .logout-btn { padding: 5px 10px; background: #333; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>楽譜管理アプリ</h1>
    <form method="GET" action="/logout" class="logout">
        <button type="submit" class="logout-btn">ログアウト</button>
    </form>
    <div style="clear: both;"></div>

    <form method="POST" action="{{ url_for('add') }}">
        <h2>楽譜を追加</h2>
        <label>ID: <input type="text" name="song_id" required></label>
        <label>楽曲名: <input type="text" name="title" required></label>
        <label>作曲者: <input type="text" name="composer"></label>
        <label>ジャンル: <input type="text" name="genre"></label>
        <label>振り分け番号: <input type="text" name="number"></label>
        <label>備考: <textarea name="notes"></textarea></label>
        <button type="submit">追加</button>
    </form>

    <h2>検索</h2>
    <form method="GET" action="/">
        <input type="text" name="q" placeholder="キーワード検索" value="{{ query }}">
        <button type="submit">検索</button>
    </form>

    <h2>登録された楽譜</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>楽曲名</th>
            <th>作曲者</th>
            <th>ジャンル</th>
            <th>振り分け番号</th>
            <th>備考</th>
            <th>操作</th>
        </tr>
        {% for score in scores %}
        <tr>
            <td>{{ score[1] }}</td>
            <td>{{ score[2] }}</td>
            <td>{{ score[3] }}</td>
            <td>{{ score[4] }}</td>
            <td>{{ score[5] }}</td>
            <td>{{ score[6] }}</td>
            <td>
                <form method="POST" action="{{ url_for('delete', score_id=score[0]) }}">
                    <button type="submit" class="delete-btn">削除</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""
# --- ログインページ ---
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        password = request.form["password"]
        if password == "seiko":  # ←ここを好きなパスワードに変更
            session["logged_in"] = True
            return redirect("/")
        else:
            error = "パスワードが違います"
    return render_template_string(LOGIN_TEMPLATE, error=error)

# --- ログアウト ---
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/login")

# --- メイン画面 ---
@app.route("/", methods=["GET"])
def index():
    if not session.get("logged_in"):
        return redirect("/login")

    query = request.args.get("q", "")
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    if query:
        c.execute("""SELECT * FROM scores 
                     WHERE song_id LIKE ? OR title LIKE ? OR composer LIKE ? 
                     OR genre LIKE ? OR number LIKE ? OR notes LIKE ?""",
                  tuple([f"%{query}%"]*6))
    else:
        c.execute("SELECT * FROM scores")
    scores = c.fetchall()
    conn.close()
    return render_template_string(TEMPLATE, scores=scores, query=query)

# --- 追加 ---
@app.route("/add", methods=["POST"])
def add():
    if not session.get("logged_in"):
        return redirect("/login")

    song_id = request.form["song_id"]
    title = request.form["title"]
    composer = request.form.get("composer", "")
    genre = request.form.get("genre", "")
    number = request.form.get("number", "")
    notes = request.form.get("notes", "")

    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute("INSERT INTO scores (song_id, title, composer, genre, number, notes) VALUES (?, ?, ?, ?, ?, ?)",
              (song_id, title, composer, genre, number, notes))
    conn.commit()
    conn.close()
    return redirect("/")

# --- 削除 ---
@app.route("/delete/<int:score_id>", methods=["POST"])
def delete(score_id):
    if not session.get("logged_in"):
        return redirect("/login")

    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute("DELETE FROM scores WHERE id=?", (score_id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
