from flask import Flask, render_template_string, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "gcfgyhjbvghjnb"

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
    <title>吹奏楽部-譜面管理-</title>
    <style>
        body { background-color: #add8e6; font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        form { margin-bottom: 20px; }
        input[type=text] { padding: 5px; margin: 3px; width: 200px; }
        input[type=submit] { padding: 5px 15px; margin: 5px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #666; padding: 8px; text-align: left; }
        th { background-color: #ddd; }
        .delete-btn { background: red; color: white; border: none; padding: 5px 10px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>吹奏楽部-譜面管理-</h1>

    <h2>楽譜の追加</h2>
    <form method="POST" action="/add">
        <input type="text" name="song_id" placeholder="ID" required>
        <input type="text" name="title" placeholder="楽曲名" required>
        <input type="text" name="composer" placeholder="作曲者">
        <input type="text" name="genre" placeholder="ジャンル">
        <input type="text" name="number" placeholder="振り分け番号">
        <input type="text" name="notes" placeholder="備考">
        <input type="submit" value="追加">
    </form>

    <h2>検索</h2>
    <form method="GET" action="/">
        <input type="text" name="q" placeholder="キーワード検索" value="{{ query }}">
        <input type="submit" value="検索">
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
                <form method="POST" action="/delete/{{ score[0] }}" style="display:inline;">
                    <input type="submit" class="delete-btn" value="削除">
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
