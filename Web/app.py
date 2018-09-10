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

@app.route('/')
def index():
    return render_template('index.html')


def video_stream(camera):
    while(1):
        data = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')


@app.route('/camera')
def camera():
    return Response(video_stream(ca.MyCamera()),mimetype='multipart/x-mixed-replace; boundary=frame')


#when the web service is over
#@app.teardown_appcontext
#def close_db(error):
    #if hasattr(g,'sqlite_db'):
        #g.sqlite_db.close()



if __name__ == '__main__':
    app.run(threaded=True)