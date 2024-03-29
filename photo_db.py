import re, photo_file, photo_sqlite
from photo_sqlite import exec, select

# create new album, put new album into album table and return id
def album_new(user_id,args):
	name = args.get("name","")
	if name == "": return 0
	album_id = exec(
		"INSERT INTO albums (name,user_id) VALUES(?,?)", name,user_id)
	return album_id

# get album of specific user
def get_albums(user_id):
	return select("SELECT * FROM albums WHERE user_id=?",user_id)

# get album info
def get_album(album_id):
	a = select("SELECT * FROM albums WHERE album_id=?",album_id)
	if len(a) == 0: return None
	return a[0]

def get_album_name(album_id):
	a = get_album(album_id)
	if a == None: return "No category"
	return a["name"]

def save_file(user_id, upfile, album_id):
	if not re.search(r'\.(jpg|jpeg)$',upfile.filename):
		print("not JPEG: ",upfile.filename)
		return 0
	if album_id == 0:
		a = select("SELECT * FROM albums " + "WHERE user_id=? AND albums" + user_id, "No category")
		if len(a) == 0:
			album_id = exec("INSERT INTO albums" + "(user_id,name) VALUES(?,?)",user_id,"No Category")
		else:
			album_id = a[0]["album_id"]
	file_id = exec('''
			INSERT INTO fils(user_id,filename,album_id) VALUES (?,?,?)''',
			user_id,upfile.filename,album_id)
	upfile.save(photo_file.get_path(file_id))
	return file_id

def get_file(file_id,ptype):
	a = select("SELECT * FROM files WHERE file_id=?",file_id)
	if len(a) == 0: return None
	p = a[0]
	p["path"] = photo_file.get_path(file_id)
	if ptype == "thumb":
		p["path"] = photo_file.make_thumbnail(file_id,300)
	return p

def get_files():
	a = select("SELECT * FROM files " + "ORDER BY file_id DESC LIMIT 50")
	for i in a:
		i["name"] = get_album_name(i["album_id"])
	return a

def get_album_files(album_id):
	return select("""
				SELECT * FROM files WHERE album_id = ? ORDER BY file_id DESC """, album_id)

def get_user_files(user_id):
	a = select(""" SELECT * FROM files WHERE user_id =? ORDER BY file_id DESC LIMIT 50""",user_id)
	for i in a:
		i["name"] = get_album_name(i["album_id"])
	return a
	
