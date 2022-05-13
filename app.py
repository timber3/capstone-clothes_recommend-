from distutils.log import debug
import os
from datetime import datetime
from unicodedata import name
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = '\static\image'
ALLOWED_EXTENSION = {'txt', 'png', 'jpg', 'jpeg', 'gif'}

path = "static/image/"
file_list = os.listdir(path)
count = len(file_list)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///imgname.db' #가상의 db생성 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

class dbimg(db.Model):
    id = db.Column('img_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    
    def __init__(self, name):
        self.name = name


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/button_tem')
def button_tem():
    return render_template('button_tem.html')

@app.route('/select_image')
def select_image():
    file_list = os.listdir(path)
    count = len(file_list)
    return render_template('select_image.html', file_list=file_list, count=count, dbimg = dbimg.query.all())

@app.route('/single_move')
def single_move():
    return render_template('single_move.html')

@app.route('/upload')
def render_file():
    return render_template('upload.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSION

@app.route('/index', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f and allowed_file(f.filename):
        # 저장할 경로 + 파일명
            f.save("./static/image/"+secure_filename(f.filename))
            temp = secure_filename(f.filename)
            imagename = dbimg(f.filename)
            db.session.add(imagename)
            db.session.commit()
            return render_template('index.html', Testname = temp)
    return render_template('index.html' , error = "사진 파일 에러")

@app.route('/new', methods = ['GET', 'POST'])
def new():
    if request.method == 'POST':
        imagename = dbimg(request.form['name'])
         
        db.session.add(imagename)
        db.session.commit()
        flash('Record was successfully added')
        return redirect(url_for('select_image'))
    return render_template('new.html')
 
@app.route('/remove', methods = ['GET', 'POST'])
def remove():
    if request.method == 'POST':
        imagename = dbimg.query.filter_by(name = request.form['name']).first()
        db.session.delete(imagename)
        db.session.commit()
        return redirect(url_for('select_image'))
    return render_template('remove.html')
 
if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=9999, debug = True)
