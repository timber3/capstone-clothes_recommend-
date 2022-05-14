from distutils.log import debug
import os
from datetime import datetime
from unicodedata import name
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from ast import literal_eval
import pandas as pd
import numpy as np
import warnings
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

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

#-----------------------------------------------------------------------------------------------------------
warnings.filterwarnings(action='ignore')

clothes = pd.read_csv('C:/Users/user/Desktop/content-based/5000_style2.csv', encoding='utf-8')
clothes_df = clothes[['id','gender','masterCategory','subCategory','articleType','baseColour','season','allcover']]
cnt_vect = CountVectorizer(min_df=0, ngram_range=(1,2))
clothes_vect = cnt_vect.fit_transform(clothes_df['allcover'])
clothes_sim = cosine_similarity(clothes_vect, clothes_vect)
clothes_sim_idx = (-clothes_sim).argsort()[::]

def find_sim_clothes(df, sorted_idx, item_id, top_n=10):
    title_clothes = df[df['id'] == item_id]
    title_clothes_idx = title_clothes.index.values
    top_sim_idx = sorted_idx[title_clothes_idx, :top_n]
    top_sim_idx = top_sim_idx.reshape(-1,)
    similar_clothes = df.iloc[top_sim_idx]
    
    return similar_clothes



db = SQLAlchemy(app)

class dbimg(db.Model):
    id = db.Column('img_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    
    def __init__(self, name):
        self.name = name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(100))
    password = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    
    # def __init__(self,  userid, password, gender):
    #     self.userid = userid
    #     self.password = password
    #     self.gender = gender
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)




@app.route('/')
def main():
    userid = session.get('userid',None)
    return render_template('index.html', userid = userid)

@app.route('/button_tem')
def button_tem():
    return render_template('button_tem.html')

@app.route('/register')
def register():
    return render_template('register.html')

   
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/recommend')
def recommend():
    similar_clothes = find_sim_clothes(clothes_df, clothes_sim_idx, 30805)
    file_list = similar_clothes[['id','gender','subCategory','articleType','baseColour']]
    count = len(file_list)
    
    return render_template('recommend.html', file_list=file_list, count=count)

@app.route('/select_image')
def select_image():
    file_list = os.listdir(path)
    count = len(file_list)
    return render_template('select_image.html', file_list=file_list, count=count, dbimg = dbimg.query.all())

@app.route('/register', methods=['POST']) #GET(정보보기), POST(정보수정) 메서드 허용
def register2():
    userid = request.form.get('userid')
    gender = request.form.get('gender')
    password = request.form.get('password')
    print(userid, gender, password)
    if not(userid and gender and password):
        return "입력되지 않은 정보가 있습니다"
    else:
        usertable = User()
        usertable.userid = userid
        usertable.gender = gender
        usertable.password = password
        print(userid, gender, password)
        db.session.add(usertable)
        db.session.commit()
        return "회원가입 성공"
    return redirect('/')

@app.route('/login', methods=['POST']) #GET(정보보기), POST(정보수정) 메서드 허용
def login2():
    userid = request.form.get('userid')
    password = request.form.get('password')
    
    session['userid'] = userid
    return redirect('/')

    
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
    app.run(host='0.0.0.0', port=8080, debug = True)
