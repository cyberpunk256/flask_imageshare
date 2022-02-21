from flask import Flask,redirect,request
from flask import render_template,send_file
import photo_db,sns_user as user

app = Flask(__name__)
app.secret_key = "abcdef"

@app.route("/login")
def login():
	return render_template("login_form.html")

@app.route("/login/try",methods=["POST"])
def login_try():
	ok = user.try_login(request.form)
	if not ok: return msg("Login fail")
	return redirect("/")

@app.route("/logout")
def logout():
	user.try_logout()
	return msg("Logout")

# login is necessary
@app.route("/")
@user.login_required
def index():
	return render_template("index.html",id=user.get_id(),photos=photo_db.get_files())

@app.route("/album/<album_id>")
@user.login_required
def user_page(user_id):
	return render_template("user.html",id=user_id,photos=photo_db.get_user_files(user_id))

@app.route("/upload")
@user.login_required
def upload():
	return render_template("upload_form.html",albums=photo_db.get_albums(user.get_id()))

@app.route("/upload/try",methods=["POST"])
@user.login_required
def upload_try():
	upfile = request.files.get("upfile",None)
	if upfile is None: return msg("Upload fail")
	if upfile.filename == "": return msg("Upload fail")
	album_id = int(request.form.get("album","0"))
	photo_id = photo_db.save_file(user.get_id(),upfile,album_id)
	if photo_id == 0: return msg("database error")
	return redirect("/user/" + str(user.get_id()))

@app.route("/album/new")
@user.login_required
def album_new():
	return render_template("album_new_form.html")

@app.route("/album/new/try")
@user.login_required
def album_new_try():
	id = photo_db.album_new(user.get_id(),request.args)
	if id == 0: return msg("new album fail")
	return redirect("/upload")

@app.route("/photo/<file_id>")
@user.login_required
def photo(file_id):
	ptype = request.args.get("t","")
	photo = photo_db.get_file(file_id,ptype)
	if photo is None: return msg("no file")
	return send_file(photo["path"])

def msg(s):
	return render_template("msg.html",msg=s)

@app.context_processor
def add_staticfile():
	return dict(staticfile=staticfile_cp)

def staticfile_cp(fname):
	import os
	path = os.path.join(app.root_path,"static",fname)
	mtime = str(int(os.stat(path).st_mtime))
	return "/static/" + fname + "?v=" + str(mtime)

if __name__ == "__main__":
	app.run(debug=True,host="0.0.0.0")