# -*- coding: utf-8 -*-
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from postmarkup import render_bbcode
import random
import urllib2
import re
from time import time as unixtime

# configuration
DATABASE = 'blog.db'
DEBUG    = True
USERNAME = "admin"
ADMINNAME = "OBEY!"  # The name which will automatically fill in the nickname in the comment submission
PASSWORD = "password"
BLOGS_PER_FRONTPAGE = 5
SECRET_KEY= "H8\x93t\xe6\x1c\xd9\x83\xca\x15\xafO\x81\x15\xd9j\xdc'\xa8\x1f\x811@$"

app = Flask(__name__)
app.config.from_object(__name__)

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    if 'session_id' not in session:
        session['session_id'] = hex(random.randint(60000000,100000000))[2:]
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

def query_db(query, args=(), one=False,renderbbcode=True):
    """Queries the database and returns a list of dictionaries."""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    if rv and renderbbcode:
        for d in rv:
            if 'text' in d and 'title' in d:
                d['text'] = render_bbcode(str(d['text']))
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def frontpage():
    page = request.args.get('page')
    if page == None:
        page = 0
    else:
        page = int(page)

    blogs = query_db("""
  SELECT post.*, COUNT(comment.commentpage) AS comments 
  FROM post LEFT OUTER JOIN comment 
  ON comment.commentpage=post.id AND comment.removed!=1
    WHERE post.removed!=1
  GROUP BY post.id
  ORDER BY post.id DESC LIMIT ? OFFSET ?; """,[BLOGS_PER_FRONTPAGE+1,(BLOGS_PER_FRONTPAGE*page)])
    g.blogs = blogs[:BLOGS_PER_FRONTPAGE]
    if len(blogs) == BLOGS_PER_FRONTPAGE+1:
        older_blogs = True
    else:
        older_blogs = False
    if len(g.blogs) == 0: abort(404)
    return render_template("frontpage.html",older_blogs=older_blogs,page=page)

@app.route('/addblog')
def add_blog():
    if 'logged_in' in session:
        if not request.args.get("recover") == "1":
            return render_template("addpost.html")
        else:
            title = request.args.get('title')
            blogpost = request.args.get('blogpost')
            preview = request.args.get("preview")
            if preview == "1":
                renderedblog = render_bbcode(blogpost)
                return render_template("addpost.html",preview=preview,title=title,blogpost=blogpost,renderedblog=renderedblog)
            else:
                return render_template("addpost.html",preview=preview,title=title,blogpost=blogpost)

    else:
        return abort(403);

@app.route('/commitblog', methods=['POST'])
def commitblog():
    if 'logged_in' in session:
        title = request.form['title'].strip()
        blogpost = request.form['blogpost'].strip()

        if 'Preview Blog' in request.form.values():
            return redirect(url_for('add_blog',preview=1,title=title,blogpost=blogpost,recover=1))

        error = 0
        if title == "":
            error = 1
            flash("You must make a title","error")
        if blogpost == "":
            error = 1
            flash("You must make the blogpost","error")

        if error:
            return redirect(url_for('add_blog',title=title,blogpost=blogpost,recover=1))
        time_var = unixtime()
        g.db.execute("""
INSERT INTO post (title, text, removed,unixtime,views) VALUES (?,?,0,?,0)
""",(title,blogpost,time_var))
        g.db.commit()
        blogid = query_db("""SELECT id FROM post WHERE unixtime=?""",[time_var],True)['id']
    else:
        return abort(403)
    return redirect(url_for('blogpost',blogid=blogid))

@app.route('/blogedit/<int:blogid>',methods=['POST','GET'])
def blogedit(blogid):
    if 'logged_in' not in session:
        abort(403)
    if request.method == 'POST':
        title = request.form['title'].strip()
        text  = request.form['blogpost'].strip()

        error = 0
        if title == "":
            error = 1
            flash("You must make a title","error")
        if text == "":
            error = 1
            flash("You must make the blogpost","error")
        if 'Preview Blog' in request.form.values():
            renderedblog = render_bbcode(text)
            return render_template("blogedit.html",blogid=blogid,title=title,blogpost=text,recover=1,preview="1",renderedblog=renderedblog)
        if error:
            return render_template('blogedit.html',blogid=blogid,title=title,blogpost=text,recover=1)

        g.db.execute("""
UPDATE post SET title=?, text=?, lastedit=? WHERE id=?
""",(title,text,unixtime(),blogid))
        g.db.commit()
        flash("You successfully changed your blogpost","message")
        return redirect(url_for('blogpost',blogid=blogid))
    g.blog = query_db("""
SELECT * FROM post WHERE id=?
""", [str(blogid)], True,False)
    return render_template('blogedit.html',blogid=blogid)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            flash('Invalid password and/or invalid username','error')
        elif request.form['password'] != app.config['PASSWORD']:
            flash('Invalid password and/or invalid username','error')
        else:
            session['logged_in'] = True
            flash('You were logged in','message')
            return redirect(url_for('frontpage'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out','message')
    return redirect(url_for('frontpage'))

@app.route('/about')
def about():
    g.about = render_bbcode(query_db("""
SELECT text FROM about LIMIT 1
""",(),True)['text'])
    return render_template("about.html")

@app.route('/blogpost/<int:blogid>')
def blogpost(blogid):
    g.blog = query_db("""
SELECT * FROM post WHERE id=? AND removed!=1
""", [str(blogid)], True)

    g.comments = query_db("""
SELECT * FROM comment WHERE commentpage=? AND removed=0 ORDER BY id DESC
""",[str(blogid)])

    if g.blog == None:
        abort(404)
    if not request.args.get("recover") == "1":
        g.db.execute("""
UPDATE post SET views = (views + 1) WHERE id=?
""",[str(blogid)])
        g.db.commit()	
        return render_template('blogpost.html',blogid=blogid,adminuser=ADMINNAME)
    else:
        website  = request.args.get('website')
        nickname = request.args.get('nickname')
        comment  = request.args.get('comment')
        email    = request.args.get('email')
        return render_template('blogpost.html',blogid=blogid,website=website,nickname=nickname,comment=comment,email=email)

@app.route("/commitcomment/<int:blogid>",methods=["POST"])
def commitcomment(blogid):
    error = 0
    website = request.form['website'].strip()
    nickname = request.form['nickname'].strip()
    comment = request.form['comment'].strip()
    email = request.form['email'].strip()
    ispublic = {'public':1,'nopublic':0}[request.form['ispublic']]

    if 'logged_in' in session:
        admin = 1
    else:
        admin = 0
        answer = request.form['captchaanswer']
        correct = int(urllib2.urlopen('http://captchator.com/captcha/check_answer/'+session['session_id']+'/'+answer).read(100))

    if ispublic not in (0,1):
        ispublic = 0

    ip = request.remote_addr

    if admin or correct:
        if nickname == "":
            error = 1
            flash('You must fill in your name!','error')
        elif len(nickname) > 50:
            error = 1
            flash("Your name may be no longer than 50 characters long.","error")
        if comment == "":
            error = 1
            flash('You must make a comment!','error')
        elif len(comment) > 1500:
            error = 1
            flash('You may not write a comment longer than 1500 characters. The one you submitted has '+str(len(comment))+" characters.","error")
        if email != "" and not re.match('.*@.*\..*',email):
            error = 1
            flash("Please only submit a valid email address. (email is optional)","error")
        if not error:
            flash("You made a comment!",'message')
            g.db.execute("""
INSERT INTO comment (commentpage, commenttext,nickname,website,email,removed,unixtime,ip,publicemail,isadmin) 
              VALUES(?,           ?,          ?,       ?,      ?,    0,      ?,       ?, ?,          ?)
""",(blogid,comment,nickname,website,email,unixtime(),ip,ispublic,admin))
            g.db.commit()
    else:
        error = 1
        flash('Your answer to the image test was incorrect.','error')
    if error:
        return redirect(url_for('blogpost',blogid=blogid,recover=1,website=website,nickname=nickname,comment=comment,email=email))
    else:
        return redirect(url_for('blogpost',blogid=blogid))

@app.route('/delete/<what>/<int:whatid>')
def delete(what,whatid):
    if 'logged_in' not in session:
        abort(403)
    returnto_ip = request.args.get('returnto_ip')
    returnto_manage_comments = request.args.get('returnto_manage_comments')

    if what == "blogpost":
        g.db.execute(""" 
UPDATE post SET removed=1, timeofremoval=? WHERE id=?
""",[unixtime(),whatid])
        g.db.commit()
        flash("The blogpost has been deleted <a class='undo_recover' href='"+ url_for("recover",what="blogpost",whatid=whatid) +"'>Undo deletion</a>","message")
        return redirect(url_for("frontpage"))
    elif what == "comment":
        commentpage = query_db("""
SELECT commentpage FROM comment WHERE id=?
""",[whatid])[0]["commentpage"]
        g.db.execute("""
UPDATE comment SET removed=1, timeofremoval=? WHERE id=?
""",[unixtime(),whatid])
        g.db.commit()

        if not returnto_ip and not returnto_manage_comments:
            flash("The comment has been deleted <a class='undo_recover' href='"+ url_for("recover",what="comment",whatid=whatid) +"'>Undo deletion</a>","message")
            return redirect(url_for("blogpost",blogid=commentpage))
        elif returnto_manage_comments:
            flash("The comment has been deleted <a class='undo_recover' href='"+ url_for("recover",what="comment",whatid=whatid,returnto_manage_comments=returnto_manage_comments) +"'>Undo deletion</a>","message")
            return redirect(url_for('comments_for',blogpost=returnto_manage_comments))
        else:
            flash("The comment has been deleted <a class='undo_recover' href='"+ url_for("recover",what="comment",whatid=whatid,returnto_ip=returnto_ip) +"'>Undo deletion</a>","message")
            return redirect(url_for("comments_by",ipaddress=returnto_ip))
    elif what == "draft":
        
        g.db.execute("""
UPDATE draft SET removed=1, timeofremoval=? WHERE id=?
""",[unixtime(),whatid])
        g.db.commit()
        flash("The draft has been removed <a class='undo_recover' href='"+ url_for("recover",what="draft",whatid=whatid) +"'>Undo deletion</a>","message")

        return redirect(url_for('drafts'))
    else:
        abort(404)

@app.route('/recover/<what>/<int:whatid>')
def recover(what,whatid):
    if 'logged_in' not in session:
        abort(403)
    returnto_ip = request.args.get('returnto_ip')
    returnto_manage_comments = request.args.get('returnto_manage_comments')

    if what == "blogpost":
        g.db.execute("""
UPDATE post SET removed=0, timeofremoval=0 WHERE id=?
""",[whatid])
        g.db.commit()
        flash("The blogpost has now been recovered","message")
        return redirect(url_for("blogpost",blogid=whatid))

    elif what == "comment":
        blogpost = query_db("""
SELECT commentpage FROM comment WHERE id=?
""",[whatid],True)
        g.db.execute("""
UPDATE comment SET removed=0 WHERE id=?
""",[whatid])
        g.db.commit()
        flash("The comment has now been recovered","message")
        if not returnto_ip and not returnto_manage_comments:
            return redirect(url_for("blogpost",blogid=blogpost['commentpage']))
        elif returnto_manage_comments:
            return redirect(url_for('comments_for',blogpost=returnto_manage_comments))
        else:
            return redirect(url_for("comments_by",ipaddress=returnto_ip))

    elif what == "draft":
        g.db.execute("""
UPDATE draft SET removed=0 WHERE id=?
""",[whatid])
        g.db.commit()
        flash("Your draft has been recovered","message")
        return redirect(url_for('drafts'))
    else:
        abort(404)

@app.route("/editabout",methods=['GET','POST'])
def editabout():
    if "logged_in" not in session:
        abort(403)
    if request.method == "POST":
        blogpost = request.form['blogpost']
        if 'Preview Aboutpage' in request.form.values():
            return render_template("editabout.html",preview="1",renderedblog=render_bbcode(blogpost),blogpost=blogpost,recover=1)

        g.db.execute("""
UPDATE about SET text=?, unixtime=?
""",[blogpost,unixtime()])
        g.db.commit()
        flash("You have successfully edited the aboutpage","message")
        return redirect(url_for("about"))

    g.orig_about = query_db("""
SELECT text FROM about LIMIT 1
""",(),True)['text']
    return render_template("editabout.html")

@app.route('/comments_by/<ipaddress>')
def comments_by(ipaddress):
    if not 'logged_in' in session:
        abort(403)
    g.comments = query_db("""
SELECT c.*, b.title AS blogtitle, b.removed AS isblogremoved
FROM comment AS c 
 LEFT OUTER JOIN post AS b 
   ON b.id=c.commentpage 
WHERE c.ip=?
GROUP by c.id 
ORDER by c.id DESC;
""",[ipaddress])

    return render_template("comments_by.html",ipaddress=ipaddress)

@app.route('/manage_comments_for/<int:blogpost>')
def comments_for(blogpost):
    if not 'logged_in' in session:
        abort(403)

    g.blog = query_db("""
SELECT title, id FROM post
WHERE id=?
LIMIT 1
""",[blogpost])

    g.comments = query_db("""
SELECT *
FROM comment
WHERE commentpage=?
ORDER BY id DESC;
""",[blogpost])
    return render_template("manage_comments_for.html")

@app.route('/comment/<int:commentid>')
def comment(commentid):
    
    g.comment = query_db("""
SELECT c.*, b.title AS blogtitle, b.removed AS isblogremoved
FROM comment AS c 
 LEFT OUTER JOIN post AS b 
   ON b.id=c.commentpage 
WHERE c.id=?
GROUP BY c.id 
""",[commentid],True)

    return render_template("comment.html")

@app.route('/drafts')
def drafts():
    if 'logged_in' not in session:
        abort(403)

    g.drafts = query_db("""
SELECT * FROM draft WHERE removed=0 ORDER BY lastedit DESC
""")
    return render_template("drafts.html")

@app.route('/adddraft',methods=['post'])
def adddraft():
    if 'logged_in' not in session:
        abort(403)

    blogpost = request.form['blogpost']
    title = request.form['title']

    g.db.execute("""
INSERT INTO draft(title,text,removed,lastedit) VALUES(?,?,0,?)
""",[title,blogpost,unixtime()])
    g.db.commit()
    flash("You saved a new draft.","message")
    return redirect(url_for('drafts'))

@app.route('/editdraft/<int:draftid>',methods=['POST','GET'])
def editdraft(draftid):
    if 'logged_in' not in session:
        abort(403)

    if request.method == "POST":
        blogpost = request.form['blogpost']

        title = request.form['title']
        if 'Preview Draft' in request.form.values():
            return render_template("editdraft.html",preview="1",renderedblog=render_bbcode(blogpost),title=title,blogpost=blogpost,recover=1)
        elif 'Submit Draft' in request.form.values():
            g.db.execute("""
UPDATE draft SET
title=?,
text=?,
lastedit=?
WHERE id=?
""",[title,blogpost,unixtime(),draftid])
            g.db.commit()
            flash("You have saved your draft","message")
            return redirect(url_for('drafts'))

        elif 'Publish Draft' in request.form.values():

            error = 0
            if title == "":
                error = 1
                flash("You must make a title","error")
            if blogpost == "":
                error = 1
                flash("You must make the blogpost","error")
            if error:
                return render_template('editdraft.html',title=title,blogpost=blogpost,recover=1)
            time_var = unixtime()
            g.db.execute("""
INSERT INTO post (title, text, removed,unixtime,views) VALUES (?,?,0,?,0)
""",(title,blogpost,time_var))
            g.db.commit()
            blogid = query_db("""SELECT id FROM post WHERE unixtime=?""",[time_var],True)['id']
            g.db.execute("""
DELETE FROM draft WHERE id=?
""",[draftid])
            g.db.commit()
            flash("You have published a draft","message")

            return redirect(url_for('blogpost',blogid=blogid))
            
    g.blog = query_db("""
SELECT * FROM draft WHERE id=? AND removed=0
""",[draftid],True,False)
            
    return render_template("editdraft.html")
        
if __name__ == "__main__":
    app.run(host="0.0.0.0")
