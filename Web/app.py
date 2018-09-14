#--coding:utf-8--
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, Response,make_response
from flask_sqlalchemy import SQLAlchemy
import cv2 as cv
import pymysql
import time
import camera as ca
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.emit('message', {'data':'hello!'}, namespace='/warning')


#database settings
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Lyr112358!@127.0.0.1/2018Python"
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db_user = SQLAlchemy(app)
db_root = SQLAlchemy(app)
#db_warning = SQLAlchemy(app)
class user(db_user.Model):
    __name__='user'
    username = db_user.Column(db_user.String(20), primary_key=True)
    password = db_user.Column(db_user.String(20))

    def __init__(self, username,password):
        self.password = password
        self.username = username

    def __repr__(self):
       return '<username %r,password %r>' % (self.username,self.password)


class rootuser(db_root.Model):
    __name__='rootuser'
    username = db_root.Column(db_root.String(20), primary_key=True)
    password = db_root.Column(db_root.String(20))

    def __init__(self, username,password):
        self.password = password
        self.username = username

    def __repr__(self):
       return '<username %r,password %r>' % (self.username,self.password)


#class warning(db_warning.Model):
#    __name__='warning'
#    id = db_root.Column(db_warning.INT(), primary_key=True,autoincrement=True)
#    message = db_root.Column(db_warning.String(255))

#    def __init__(self, id,message):
#        self.id = id
#        self.message = message

#    def __repr__(self):
#       return '<id %d,message %r>' % (self.id,self.message)

#test1 = rootuser('root','1234')
#db_root.session.add(test1)
#db_root.session.commit()

#ret = db_root.session.query(rootuser).filter_by(username='root').first()
#print(ret)
#print(ret.username)
#print(ret.password)


m_camera = ca.MyCamera(socketio,app)

@app.route('/warning')
def warning():
    info = request.args.get('msg')
    print('\n in@:' + info +'\n')
    socketio.emit('message', info ,namespace='/warning')
    return "warning has sent"


@app.route('/')
def index():
    username = request.cookies.get('username')
    if username:
        return redirect('/function_list')
    login = request.cookies.get('login')
    if login == 'root':
        return render_template('login.html', entries={'root': True})
    else:
        return render_template('login.html', entries={'root': False})



@app.route('/login_swift',methods=['POST'])
def login_swift():
    login = request.cookies.get('login')
    res = redirect('/')
    if login == 'root':
        res.set_cookie('login','')
    else:
        res.set_cookie('login','root')
    return res


@app.route('/login',methods=['POST'])
def check_login():
    login = request.cookies.get('login')
    name = request.form.get('name')
    pwd = request.form.get('password')
    if login == 'root':
        ret = db_root.session.query(rootuser).filter_by(username=name).first()
        if ret:
            if ret.password == pwd:
                resp = redirect('/function_list')
                resp.set_cookie('username',name)
                resp.set_cookie('password', pwd)
                return resp
        return redirect('/')
    else:
        ret = db_user.session.query(user).filter_by(username=name).first()
        if ret:
            if ret.password == pwd:
                resp = redirect('/function_list')
                resp.set_cookie('username', name)
                resp.set_cookie('password', pwd)
                return resp
        return redirect('/')


@app.route('/logout',methods=['POST'])
def logout():
    res = redirect('/')
    res.set_cookie('username','')
    res.set_cookie('password','')
    return res

@app.route('/change_password')
def change_password():
    username = request.cookies.get('username')
    if not username:
        return redirect('/')
    return render_template('change_password.html', entries={'name': username})


@app.route('/new_password',methods=['POST'])
def set_new_password():
    name = request.cookies.get('username')
    pwd = request.cookies.get('password')
    old_pwd = request.form.get('old_password')
    new_pwd = request.form.get('new_password')
    new_pwd2 =  request.form.get('new_password2')
    if pwd != old_pwd:
        return render_template('notice.html',entries={'info': u'原密码输入错误!'})
    else:
        if new_pwd != new_pwd2:
            return render_template('notice.html',entries={'info': u"两次密码输入不一致!"})
        else:
            login = request.cookies.get('login')
            resp = make_response(render_template('notice.html', entries={'info': u"修改成功!"}))
            resp.set_cookie('password', new_pwd)
            if login == 'root':
                ret = db_root.session.query(rootuser).filter_by(username=name).first()
                ret.password = new_pwd
                db_root.session.commit()
                return resp
            else:
                ret = db_user.session.query(user).filter_by(username=name).first()
                ret.password = new_pwd
                db_user.session.commit()
                return resp


@app.route('/function_list')
def function_list():
    username = request.cookies.get('username')
    if not username:
        return redirect('/')
    login = request.cookies.get('login')
    if login == 'root':
        return render_template('function.html',entries={'root':True})
    else:
        return render_template('function.html', entries={'root': False})


@app.route('/pure_stream')
def pure_stream():
    username = request.cookies.get('username')
    if not username:
        return redirect('/')
    return render_template('index.html',entries={'video_id':1})


@app.route("/root_add")
def root_add():
    login = request.cookies.get('login')
    if login == 'root':
        return render_template('root.html',entries={'root_op':1})
    else:
        return redirect('/')


@app.route('/root_add_new_user',methods=["POST"])
def root_add_new_user():
    name = request.form.get('username')
    pwd = request.form.get('password')
    ret = db_user.session.query(user).filter_by(username=name).first()
    if ret:
        return render_template('notice.html',entries={'info': u'用户名已存在,请重新输入用户名！'})
    else:
        new_user = user(name,pwd)
        db_user.session.add(new_user)
        db_user.session.commit()
        return render_template('notice.html',entries={'info': u'新用户添加成功！'})


@app.route('/root_check')
def root_check():
    login = request.cookies.get('login')
    if login == 'root':
        ret = db_user.session.query(user).all()
        return render_template('root.html',entries={'root_op':2,'users':ret})
    else:
        return redirect('/')


@app.route('/root_delete_user')
def root_delete_user():
    name = request.args.get('user')
    ret = db_user.session.query(user).filter_by(username=name).first()
    db_user.session.delete(ret)
    db_user.session.commit()
    return redirect('/root_check')


@app.route('/track')
def track():
    username = request.cookies.get('username')
    if not username:
        return redirect('/')
    return render_template('index.html', entries={'video_id':2})


def video_stream(camera):
    while(1):
        data = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')


def trace_moving_object_stream(camera):
    while(1):
        data = camera.get_tracking_frame()
        if data is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')


@app.route('/track_camera')
def track_camera():
    username = request.cookies.get('username')
    if not username:
        return redirect('/')
    return Response(trace_moving_object_stream(m_camera), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/track_settings',methods=['POST'])
def track_settings():
    brightness = int(request.form.get('brightness'))
    blur = int(request.form.get('blur'))
    if brightness > 0 and brightness%2 == 1 and blur > 0 and blur < 256:
        m_camera.track_setting(blur,brightness)
    return redirect(url_for("track"))


@app.route('/track_background',methods=['POST'])
def track_reset_background():
    m_camera.t_m_o.background_ready = False
    return redirect(url_for("track"))


@app.route('/camera')
def camera():
    username = request.cookies.get('username')
    if not username:
        return redirect('/')
    return Response(video_stream(m_camera),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(threaded=True)