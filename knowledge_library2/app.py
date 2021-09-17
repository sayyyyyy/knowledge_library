import os
from flask import Flask, redirect, render_template, request, session
from flask.sessions import SessionInterface
import requests
from bs4 import BeautifulSoup
import sqlite3
import sched
import smtplib
import time
from email.mime.text import MIMEText

app = Flask(__name__)

# メール送信設定
smtp_host = 'smtp.gmail.com'
smtp_port = 465
username = 'd958956a6b650@gmail.com'
password = 'aokiseiya11'
smtp = smtplib.SMTP_SSL(smtp_host, smtp_port)
smtp.login(username, password)

# session設定
app.secret_key = 'user_id'
app.secret_key = 'list_id'
app.secret_key = 'page_id'
app.secret_key = 'search'
app.secret_key = 'name'
app.secret_key = 'list_user_id'

# db設定
sqlite3.register_adapter(list, lambda l: ';'.join([str(i) for i in l]))
sqlite3.register_converter('List', lambda s: [item.decode('utf-8')  for item in s.split(bytes(b';'))])

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
 


# メインページ　ログイン前はknowlegde libraryと表示　ログイン後はリストを選択するように
@app.route("/", methods=["GET", "POST"])
def home():
    # listがなくてもOK
    try:
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()
        list__ = db.execute("SELECT tag, list_title FROM list WHERE user_id = ?", (session["user_id"], ))
        page_list = list__.fetchall()
        sqlite.close()
    except:
        pass

    if request.method == "POST":
        # 検索機能
        if request.form.get("search_ok") == "Search!":
            if request.form.get("search"):
                sqlite = sqlite3.connect('knowledge_library.db')
                db = sqlite.cursor()
                search = db.execute("SELECT tag, list_title FROM list")
                search_list = search.fetchall()
                sqlite.close()

                sqlite = sqlite3.connect('knowledge_library.db')
                db = sqlite.cursor()
                un1 = db.execute("SELECT name FROM user WHERE id = ?", (session["user_id"], ))
                session["name"] = un1.fetchone()[0]
                sqlite.close()
                sin_page_list = []
                for i in search_list:
                    if request.form.get("search") in i[0]:
                        #return i[1]
                        sin_page_list.append(i[1])
                session["search"] = sin_page_list
                return redirect("/search")
            else:
                return render_template("error.html", error_detail="Search", error_message="検索内容を入力してください")

        if request.form.get("send"):
            for i in page_list:
                if request.form.get("send") in i[1]:
                    sqlite = sqlite3.connect('knowledge_library.db')
                    db = sqlite.cursor()
                    check = db.execute("SELECT id FROM list WHERE user_id = ? AND list_title = ?", (session["user_id"], i[1]))
                    check2 = check.fetchone()[0]
                    session["list_id"] = check2
                    sqlite.close()
                    return redirect("/list")
        if request.form["search_ok"] == "Search!":
            return "aaa"
        return render_template("error.html", error_detail="Search", error_message="該当する要素がありません")
    else:
        # セッションがなかったらログイン画面にとばす
        if not "user_id" in session:
            return render_template("login.html")
        else:
            sqlite = sqlite3.connect('knowledge_library.db')
            db = sqlite.cursor()        
            username = db.execute("SELECT name FROM user WHERE id = ?", (session["user_id"],))
            username2 = username.fetchone()[0]
            sqlite.close()
            
            return render_template("index.html", page_list=page_list, username=username2)

@app.route("/list", methods=["GET", "POST"])
def list():
    try:
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()
        page = db.execute("SELECT url, comment, page_title FROM page WHERE list_id = ?", (session["list_id"],))
        page_title = page.fetchall()
        sqlite.close()
    except:
        page_title = ["ページがありません"]

    if not "user_id" in session:
            return render_template("login.html")
    else:
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()        
        username = db.execute("SELECT name FROM user WHERE id = ?", (session["user_id"],))
        username2 = username.fetchone()[0]
        sqlite.close()

    if request.method == "POST":
        if request.form.get("list_delete") == "リストを削除する":
            # リスト内ページの削除
            sqlite = sqlite3.connect('knowledge_library.db')
            db = sqlite.cursor()
            db.execute("DELETE FROM page WHERE list_id = ?", (session["list_id"], ))
            sqlite.commit()
            sqlite.close()

            #リストの削除
            sqlite = sqlite3.connect('knowledge_library.db')
            db = sqlite.cursor()
            db.execute("DELETE FROM list WHERE id = ?", (session["list_id"], ))
            sqlite.commit()
            sqlite.close()
            return redirect("/")

        for i in page_title:
            if request.form.get("list") in i[2]:
                return redirect(i[0])
          
    else:
        # ページタイトルとリストタイトルを取得して表示する
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()
        list_ = db.execute("SELECT list_title FROM list WHERE id = ?", (session["list_id"], ))
        list_title = list_.fetchone()[0]
        sqlite.close()

        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()
        is_you = db.execute("SELECT user_id FROM list WHERE id = ?", (session["list_id"],))
        is_you2 = is_you.fetchone()[0]
        sqlite.close()
        if not is_you2 == session["user_id"]:
            sqlite = sqlite3.connect('knowledge_library.db')
            db = sqlite.cursor()
            others = db.execute("SELECT name FROM user WHERE id = ?", (is_you2, ))
            other_user = others.fetchone()[0]
            sqlite.close()
        else:
            other_user = ""

        return render_template("list.html", page_title=page_title, list_title=list_title, username=username2, other_user=other_user)

# ログイン画面
@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        # username欄が空白の時
        if not request.form.get("username"):
            return render_template("error.html", error_detail="Login", error_message="usernameを入力してください")

        # password欄が空白の時
        elif not request.form.get("password"):
            return render_template("error.html", error_detail="Login", error_message="passwordを入力してください")

        try:
            sqlite = sqlite3.connect('knowledge_library.db')
            db = sqlite.cursor()
            rows = db.execute("SELECT * FROM user WHERE name = ?", (request.form.get("username"),))
            is_user = tuple(rows.fetchone())
        except:
            return render_template("error.html", error_detail="Login", error_message="有効なusernameを入力してください")

        if is_user[3] != request.form.get("password"):
            render_template("error.html", error_detail="Login", error_message="パスワードが違います")
        else:
            session["user_id"] = is_user[0]    
            return redirect("/")
    else:
        return render_template("login.html")

# ユーザ登録画面
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # username欄が空白の時
        if not request.form.get("username"):
            return render_template("error.html", error_detail="Resister", error_message="usernameを入力してください")
        # password欄が空白の時
        elif not request.form.get("password"):
            return render_template("error.html", error_detail="Resister", error_message="passwordを入力してください")
        # confirmation欄が空白の時
        elif not request.form.get("confirmation"):
            return render_template("error.html", error_detail="Resister", error_message="confirmationを入力してください")
        
        # email欄が空白の時
        elif not request.form.get("email"):
            return render_template("error.html", error_detail="Resister", error_message="emailを入力してください")
        # パスワードと確認用パスワードが異なる時
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", error_detail="Resister", error_message="passwordとconfirmationが異なります")
        # usernameが既に存在した時

        try:
            sqlite = sqlite3.connect('knowledge_library.db')
            db = sqlite.cursor()
            
            # userテーブルにデータを登録する
            db.execute("INSERT INTO user (name, email, password) VALUES(?, ?, ?)",
                       (request.form.get("username"), request.form.get("email"), request.form.get("password")))
            sqlite.commit()

            # データベースからidを取得してsessionに格納する
            user_id = db.execute("SELECT id FROM user WHERE name = ? AND password = ?", (request.form.get("username"), request.form.get("password")))
            session["user_id"] = user_id.fetchone()[0]
            return redirect("/")
        except:
            return render_template("error.html", error_detail="Resister", error_message="登録できませんでした。もう一度お試しください")
    else:
        return render_template("register.html")

# ログアウト画面　トップに戻るボタンを配置
@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

# 通知機能を実装
def notification_send(title, url, comment, name, email):
    message = "<strong><font color =#a59aca>" + name + "</font></strong> Did you forget? Click below to see the Page!<br><br><u>Title : </u><strong>" + title + "</strong><br>" + url + "<br><br> <u>Comment :</u> " + comment
            
    msg = MIMEText(message, "html")
    msg["Subject"] = "パスワード変更"
    msg["To"] = email
    msg["From"] = "Knowledge_Library"
    smtp.send_message(msg)

def redirect_home():
    time.sleep(3)
    return redirect("/")

# リストにページを追加する
@app.route("/add_page", methods=["GET", "POST"])
def add_page():
    if not "user_id" in session:
            return render_template("login.html")
    else:
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()        
        username = db.execute("SELECT name FROM user WHERE id = ?", (session["user_id"],))
        username2 = username.fetchone()[0]
        sqlite.close()

    if request.method == "POST":
        # urlが空白の時
        notification = 1
        if not request.form.get("url"):
            return render_template("error.html", error_detail="Add Page", error_message="urlを入力してください")
        # 通知がオフの場合
        elif not request.form.get("notification"):
            notification = 0
        
        # url先をスクレイピングしてタイトルを取得
        load_file = requests.get(request.form.get("url"))
        soup = BeautifulSoup(load_file.content, "html.parser")
        title = soup.find("title").text

        # pageテーブルにデータを追加する
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()
        db.execute("INSERT INTO page (url, page_title, comment, notification, user_id, list_id) VALUES(?, ?, ?, ?, ?, ?)",
                    (request.form.get("url"), title, request.form.get("comment"), notification, session["user_id"], session["list_id"]))
        sqlite.commit()
        sqlite.close()

        # Tag追加
        tag = []
        for i in range(1, 10):
            if request.form.get("tag_" + str(i)):
                tag.append(request.form.get("tag_" + str(i)))
            else:
                break
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()
        db.execute('UPDATE page SET tag = ? WHERE user_id = ? AND list_id = ?', (tag, session["user_id"], session["list_id"]))
        sqlite.commit()
        sqlite.close()

        if notification == 1:
            sqlite = sqlite3.connect('knowledge_library.db')
            db = sqlite.cursor()
            id_title_comment= db.execute("SELECT id FROM page WHERE user_id = ? AND list_id = ? AND url = ?", (session["user_id"], session["list_id"], request.form.get("url")))
            session["page_id"] = id_title_comment.fetchone()[0]
            id_title_comment= db.execute("SELECT page_title FROM page WHERE user_id = ? AND list_id = ? AND url = ?", (session["user_id"], session["list_id"], request.form.get("url")))
            title = id_title_comment.fetchone()[0]
            id_title_comment= db.execute("SELECT comment FROM page WHERE user_id = ? AND list_id = ? AND url = ?", (session["user_id"], session["list_id"], request.form.get("url")))
            comment = id_title_comment.fetchone()[0]
            sqlite.close()

            sqlite = sqlite3.connect('knowledge_library.db')
            db = sqlite.cursor()
            email_set = db.execute("SELECT name FROM user WHERE id = ?", (session["user_id"],))                
            name = email_set.fetchone()[0]
            email_set = db.execute("SELECT email FROM user WHERE id = ?", (session["user_id"],))     
            email = email_set.fetchone()[0]
            sqlite.close()

            redirect_home()
            time.sleep(1)
            s = sched.scheduler()
            s.enter(1, 1, notification_send, argument=(title, request.form.get("url"), comment, name, email))
            #s.enter(86400, 1, notification_send, argument=(title, url, comment, name, email))
            #s.enter(172800, 2, notification_send, argument=(title, url, comment, name, email))
            #s.enter(604800, 3, notification_send, argument=(title, url, comment, name, email))
            #s.enter(2592000, 4, notification_send, argument=(title, url, comment, name, email))
            s.run()
        return redirect("/")
        

    else:
        return render_template("add_page.html", username=username2)

@app.route("/add_list", methods=["GET", "POST"])
def add_list():
    if not "user_id" in session:
            return render_template("login.html")
    else:
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()        
        username = db.execute("SELECT name FROM user WHERE id = ?", (session["user_id"],))
        username2 = username.fetchone()[0]
        sqlite.close()

    if request.method == "POST":
        # titleが空白の時
        if not request.form.get("title"):
            return render_template("error.html", error_detail="Add List", error_message="titleを入力してください")
        elif not request.form.get("tag_1"):
            return render_template("error.html", error_detail="Add List", error_message="Tagを最低１つ入力してください")
        
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()

        # listテーブルにデータを追加する
        db.execute("INSERT INTO list (list_title, user_id) VALUES(?, ?)",
                    (request.form.get("title"), session["user_id"]))
        sqlite.commit()
        sqlite.close()
        
        # list_idをセッションに格納する
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()
        list_i = db.execute("SELECT id FROM list WHERE list_title = ? AND user_id = ?", (request.form.get("title"), session["user_id"]))
        session["list_id"] = list_i.fetchone()[0]
        sqlite.close()

        # Tag追加
        tag = []
        for i in range(1, 10):
            if request.form.get("tag_" + str(i)):
                tag.append(request.form.get("tag_" + str(i)))
            else:
                break
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()
        db.execute('UPDATE list SET tag = ? WHERE user_id = ? AND id = ?', (tag, session["user_id"], session["list_id"]))
        sqlite.commit()
        sqlite.close()

        return redirect("/")

        

    else:
        return render_template("add_list.html", username=username2)

@app.route("/lost_password", methods=["GET", "POST"])
def lost_password():
    """change password"""
    if request.method == "POST":

        # email欄が空白の時
        if not request.form.get("email"):
            return render_template("error.html", error_detail="Lost Password", error_message="emailを入力してください")

        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()
        rows = db.execute("SELECT email FROM user")
        if request.form.get("email") in rows.fetchall()[0]:
            db.execute("UPDATE user SET change_pass = ? WHERE email = ?", (1, request.form.get("email")))
            sqlite.commit()
            message = """パスワードを変更する場合は以下のURLをクリックしてください
                        http://127.0.0.1:5000/change_password
                        """
            msg = MIMEText(message, "html")
            msg["Subject"] = "パスワード変更"
            msg["To"] = request.form.get("email")
            msg["From"] = "d958956a6b650@gmail.com"
            smtp.send_message(msg)
            
            return redirect("/login")
        else:
            return render_template("error.html", error_detail="Lost Password", error_message="無効なメールアドレスです")
    return render_template("lost_password.html")

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        if not request.form.get("email"):
            return render_template("error.html", error_detail="Change Password", error_message="emailを入力してください")
        elif not request.form.get("password"):
            return render_template("error.html", error_detail="Change Password", error_message="passwordを入力してください")
        elif not request.form.get("confirmation"):
            return render_template("error.html", error_detail="Change Password", error_message="confirmationを入力してください")

        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()
        is_change = db.execute("SELECT change_pass FROM user WHERE email = ?", (request.form.get("email"),))        
        if is_change.fetchone()[0] == 1:
            if request.form.get("password") == request.form.get("confirmation"):
                sqlite = sqlite3.connect('knowledge_library.db')
                db = sqlite.cursor()
                db.execute("UPDATE user SET password = ? WHERE email = ?", (request.form.get("password"), request.form.get("email")))    
                sqlite.commit()
                sqlite.close()

                sqlite = sqlite3.connect('knowledge_library.db')
                db = sqlite.cursor()
                db.execute("UPDATE user SET change_pass = ? WHERE email = ?", (0, request.form.get("email")))    
                sqlite.commit()
                sqlite.close()
                return redirect("/login")
            else:
                return "NOT password == confirmation"
        else:
            return render_template("error.html", error_detail="Change Password", error_message="パスワード変更の申請をしてください")      
    else:
        return render_template("change_password.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    try:
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()
        list__ = db.execute("SELECT list_title FROM list")
        page_list = list__.fetchall()
        sqlite.close()
    except:
        pass

    if not "user_id" in session:
            return render_template("login.html")
    else:
        sqlite = sqlite3.connect('knowledge_library.db')
        db = sqlite.cursor()        
        username = db.execute("SELECT name FROM user WHERE id = ?", (session["user_id"],))
        username2 = username.fetchone()[0]
        sqlite.close()

    if request.method == "POST":
        if request.form.get("search_page"):
            for i in page_list:
                if request.form.get("search_page") in i[0]:
                    sqlite = sqlite3.connect('knowledge_library.db')
                    db = sqlite.cursor()
                    check = db.execute("SELECT id FROM list WHERE list_title = ?", (i[0],))
                    session["list_id"] = check.fetchone()[0]
                    sqlite.close()

                    sqlite = sqlite3.connect('knowledge_library.db')
                    db = sqlite.cursor()
                    check = db.execute("SELECT user_id FROM list WHERE list_title = ?", (i[0],))
                    session["list_user_id"] = check.fetchone()[0]
                    sqlite.close()
                    return redirect("/list")
    else:
        return render_template("search.html", is_search=request.form.get("search_page"), search_list=session["search"], username=username2)

if __name__ == "__main__":
    app.run(host='localhost', port=3000, threaded=True)    