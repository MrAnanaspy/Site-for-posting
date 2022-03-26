import datetime
from db_connect import dbinf
from flask import Flask, render_template, request, redirect, make_response

app = Flask(__name__)
app.config['SECRET_KEY'] = 'efc401bc9d6087f211d71ad9b0a673c98a70c907'


# Обработка главнлй страницы
@app.route('/')
def index():
    a = (request.cookies.get('admin'))
    if not request.cookies.get('email'):
        return render_template('home0.html')
    elif a == '0':
        return render_template('home1.html')
    else:
        return render_template('home.html')


# Обработка страницы регистрации
@app.route('/create_user', methods=['POST', 'GET'])
def create_user():
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        dat = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        dbinf("INSERT INTO users (name, password, email, date) VALUES ('%s', '%s', '%s', '%s');" % (name, password, email, dat))
        return redirect('/')
    else:

        return render_template('index.html')


# Обработка страницы с информацией о пользователях
@app.route('/users', methods=['POST', 'GET'])
def users():
    if request.method == 'GET':
        e = dbinf("SELECT * FROM `users`")
        return render_template('inform.html', articles=e)
    if request.method == "POST":
        print(request.form)
        if 'poisk' in request.form:
            req = request.form.to_dict()
            for el in req:
                print(el)
                if not request.form[el]:
                    req[el] = '%%'
                else:
                    req[el] = '%' + req[el] + '%'
            e = dbinf("SELECT * FROM users WHERE email LIKE '%s' AND name LIKE '%s'" % (req['email'], req['username']))
            return render_template('inform.html', articles=e)
        else:
            ee = request.form
            for key in ee:
                pass
            if ee[key] == 'Заблокировать':
                dbinf("DELETE FROM users WHERE id = %s" % key)
            return redirect('/users')


@app.route('/posts', methods=['POST', 'GET'])
def posts():
    e = dbinf("SELECT * FROM `Posts`")
    if request.method == "POST":
        if 'myposts' in request.form:
            cookies = (request.cookies.get('id_user'))
            qf = dbinf("SELECT * FROM `Posts` WHERE id_user = '%s'" % cookies)
            return render_template('posts.html', articles=qf)
        if 'mylike' in request.form:
            print("mylike")
            cookies = (request.cookies.get('email'))
            print(cookies)
            posid = dbinf("SELECT id_posts FROM `likes` WHERE email_user = '%s'" % (cookies))
            f = ''
            for el in posid:
                if el == posid[0]:
                    f = f + ' id = ' + str(el['id_posts'])
                f = f + ' OR id = ' + str(el['id_posts'])
                print(el)
            print(f)
            print(posid)
            ff = dbinf("SELECT * FROM `Posts` WHERE %s" % f)
            print(ff)
            return render_template('posts.html', articles=ff)
        if 'top' in request.form:
            posts_id = dbinf("SELECT id FROM `Posts`")
            idcount = {}
            for post_id in posts_id:
                count = dbinf("SELECT COUNT(*) FROM `likes` WHERE id_posts = %s" % (post_id['id']))[0]
                idcount[post_id['id']] = count['COUNT(*)']
            idcount = (dict(sorted(idcount.items(), reverse=True, key=lambda item: item[1])))
            a = []
            for key in idcount.keys():
                a = a + [key]
            toppos = dbinf('''SELECT * FROM `Posts` WHERE id = '%s' OR id = '%s' OR id = '%s' OR id = '%s' OR id = '%s' 
                            ORDER BY FIELD(id, '%s', '%s', '%s', '%s', '%s')''' % (a[0], a[1], a[2], a[3], a[4], a[0], a[1], a[2], a[3], a[4]))
            return render_template('posts.html', articles=toppos)
        if 'poisk' in request.form:
            req = request.form.to_dict()
            for el in req:
                if not request.form[el]:
                    req[el] = '%%'
                else:
                    req[el] = '%'+req[el]+'%'
            formattime = '%Y-%c-%e %T'
            eee = dbinf('''SELECT * FROM Posts WHERE 
            hashteg LIKE '%s' AND heading LIKE '%s' AND DATE_FORMAT(date, '%s') LIKE '%s' AND CONVERT(id_user,char) 
            LIKE '%s' ''' % (req['hashteg'], req['heading'], formattime, req['date'], req['author']))
            # eeee = dbinf("SELECT users.* FROM Posts, users WHERE Posts.id_user = users.id")
            return render_template('posts.html', articles=eee)

        else:
            heading = request.form['heading']
            hashteg = request.form['hashteg']
            hesh = dbinf("SELECT * FROM hashtegs WHERE name = '%s'" % hashteg)
            print(hesh)
            yo = 1
            if hesh:
                print('есть')
                num = (dbinf("SELECT uses_num FROM hashtegs WHERE name = '%s'" % hashteg))
                num = num[0]['uses_num']
                num += 1
                print(num)
                dbinf("UPDATE hashtegs SET uses_num = %s WHERE name = '%s'" % (num, hashteg))
            else:
                dbinf("INSERT INTO hashtegs (name, uses_num) VALUES ('%s', %s);" % (hashteg, yo))
            text = request.form['text']
            dat = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            iduser = request.cookies.get('id_user')
            dbinf("INSERT INTO Posts (heading, hashteg, text, date, id_user) VALUES ('%s', '%s', '%s', '%s', '%s');" % (heading, hashteg, text, dat, iduser))
        return redirect('/posts')
    else:
        return render_template('posts.html', articles=e)


@app.route('/posts/<int:id>', methods=['POST', 'GET'])
def posts_detail(id):
    likez = False
    e = dbinf("SELECT * FROM `Posts` WHERE id = '%s'" % id)
    s = dbinf("SELECT * FROM `comments` WHERE id_posts = '%s'" % id)
    kol_like = dbinf("SELECT COUNT(*) FROM `likes` WHERE `id_posts` = '%s'" % id)
    creater = dbinf('''SELECT name FROM users 
                        WHERE id in (SELECT id_user FROM Posts WHERE id = %s)''' % id)
    email_user = request.cookies.get('email')
    l = dbinf('''SELECT * FROM likes WHERE email_user = '%s' AND id_posts = %s''' % (email_user, id))
    if l:
        likez = True
    if request.method == "POST":
        if request.form['post_det'] == 'like':
            dbinf("INSERT INTO likes (id_posts, email_user) VALUES ('%s', '%s');" % (id, email_user))

        elif request.form['post_det'] == 'dislike':
            dbinf("DELETE FROM likes WHERE id_posts='%s' AND email_user = '%s';" % (id, email_user))
        else:
            user = request.cookies.get('name')
            com = request.form['post_det']
            dbinf("INSERT INTO comments (id_posts, name_users, text) VALUES ('%s', '%s', '%s');" % (id, user, com))
        return redirect('/posts/%s' % id)
    else:
        return render_template('posts_detail.html', article=e, comments=s, creater=creater, likez=likez, kol_like=kol_like[0].get('COUNT(*)'))


@app.route('/posts/<int:id>/ban', methods=['POST', 'GET'])
def posts_ban(id):
    if request.method == 'POST':
        print(request.form['ban'])
        if "ban" in request.form:
            dat = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            prich = request.form['text_ban']
            a = dbinf("SELECT * FROM `Posts` WHERE id = '%s'" % id)
            for el in a:
                d = []
                for key, value in el.items():
                    d += [value]
                ass = str(d[4])
                print("Q"+dat+"Q")
                print(type(dat))
                print("q"+ass+"q")
                print(type(ass))
                dbinf('''INSERT INTO post_pending (id_post, ban_reason, date_ban, id_user, heading, hashteg, text, date) 
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');''' % (id, prich, dat, d[5], d[1], d[2], d[3], ass))
                dbinf("DELETE FROM Posts WHERE id='%s';" % id)
                return redirect('/posts')
        else:
            return redirect('/posts/%s' % id)
    return render_template('ban.html', id=id)


@app.route('/loged', methods=['POST', 'GET'])
def loged():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        a = dbinf("SELECT id, name, email, password, admin FROM `users` WHERE email = '%s'" % email)
        for el in a:
            d = []
            for key, value in el.items():
                d += [value]
            print(d)
            if d[3] == password:
                res = make_response("Вы зарегестрированы")
                res.set_cookie('email', '%s' % email, max_age=60 * 60 * 24 * 365 * 2)
                res.set_cookie('name', '%s' % d[1], max_age=60 * 60 * 24 * 365 * 2)
                res.set_cookie('id_user', '%s' % d[0], max_age=60 * 60 * 24 * 365 * 2)
                res.set_cookie('admin', '%s' % d[4], max_age=60 * 60 * 24 * 365 * 2)
                return res
            else:
                return make_response("Неверная почта или пароль!")
    return render_template('loged.html')


@app.route('/post_pending', methods=['POST', 'GET'])
def post_pending():
    postp = dbinf("SELECT * FROM post_pending")
    if request.method == 'POST':
        if 'poisk' in request.form:
            formattime = '%Y-%c-%e %T'
            date_time = '%' + request.form['datetime'] + '%'
            print(date_time)
            postp = dbinf("SELECT * FROM post_pending WHERE DATE_FORMAT(date_ban, '%s') LIKE '%s'" % (formattime, date_time))
            return render_template('post_pending.html', pp=postp)
        for values in request.form:
            pass
        if request.form[values] == 'Вернуть':
            a = dbinf("SELECT * FROM `post_pending` WHERE id_post = %s" % values)
            d = []
            for el in a:
                for key, valuetwo in el.items():
                    d += [valuetwo]
                    print(valuetwo)
            timee = str(d[7])
            print(timee)
            dbinf('''INSERT INTO Posts (id, heading, hashteg, text, date, id_user) 
                            VALUES ('%s', '%s', '%s', '%s', '%s', '%s');''' % (d[0], d[4], d[5], d[6], timee, d[3]))
        dbinf("DELETE FROM post_pending WHERE id_post= %s;" % values)

        return redirect("/post_pending")
    return render_template('post_pending.html', pp=postp)


@app.route('/post_pending/<int:id>', methods=['POST', 'GET'])
def posts_pen_detal(id):
    e = dbinf("SELECT * FROM post_pending WHERE id_post=%s;" % id)
    print(e)
    name = e[0]["id_user"]
    print(name)
    ee = dbinf("SELECT name FROM users WHERE id=%s;" % name)
    return render_template('post_pend_det.html', id=e, ee=ee)


if __name__ == '__main__':
    app.run(debug=True)
