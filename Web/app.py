import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, Response
from flask_sqlalchemy import SQLAlchemy
import cv2 as cv
import pymysql
import time
import camera as ca


app = Flask(__name__)


#database settings
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Lyr112358!@127.0.0.1/2018Python"
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
class test(db.Model):
    __name__='test'
    id = db.Column(db.INT, primary_key=True)
    name = db.Column(db.String(20))

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
       return '<id %d,name %r>' % (self.id,self.name)


#test1 = test(2, 'Jack')
#db.session.add(test1)
#db.session.commit()

m_camera = ca.MyCamera()

@app.route('/')
def index():
    return render_template('index.html', entries={'video_id':1})

@app.route('/track')
def track():
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
    #print("in tracking")
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
    #print("in camera")
    return Response(video_stream(m_camera),mimetype='multipart/x-mixed-replace; boundary=frame')






#when the web service is over
#@app.teardown_appcontext
#def close_db(error):
    #if hasattr(g,'sqlite_db'):
        #g.sqlite_db.close()



if __name__ == '__main__':
    app.run(threaded=True)