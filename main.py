from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:no@localhost:5000/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
import re
app.secret_key = '333vdfjdo0BIEO0430nfe&*GO^AWAY&^&dfmo2349s'
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) #connects blog to user via user id 

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
    
    def _repr__(self):
        return '<blog %r>' % self.name

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True) 
    #^ unique = True makes it so the input of username can only be used once
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner') 
    #^Creats a relationship between blog and user
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '%r' % self.username



@app.route('/login', methods=['GET', 'POST'])
def login():
   
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and password:
            session['user'] = username
            return redirect('/newpost')
    if not user:
        username_error = "A Real One Please."
        return render_template('login.html', username_error=username_error)
    if not password:
        password_error = "Try Again"
        return render_template('login.html', username=username, password_error=password_error)
    

@app.before_request
def require_login():
    allowed_routes = ['index', 'get_blog', 'login', 'signup', 'single_user']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error = ''
        password_error = ''
        verify_error = ''
        username_in_db = User.query.filter_by(username=username).first()
        if username_in_db:
            username_error = 'It looks like "' + username + '" is taken. Sad day for you.'
        
        if username == '': 
            username_error = "Its either too short or too long. Figure it out."
        else:
            if not len(username) > 3 or len(username) > 20:
                username_error = "Its either too short or too long. Figure it out."
                username = ''
        if password != verify:
            password_error = ('They were not the same. Like at all.')

        if password == '':
            password_error = "Please enter a password between 3 and 20 characters."
        else:
            if not len(password) > 3 or len(password) > 20:
                password_error = "Please enter a password between 3 and 20 characters."
        if not username_error and not password_error and not verify_error:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            session['user'] = user.username
            return redirect('/newpost') 
        else:
            return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error) 
    return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    del session['user']
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def new_blog():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog = Blog(blog_title, blog_body, owner)
        title_error = ''
        body_error = ''
        if blog_title == '':
            title_error = 'Please enter a title for your blog.'
        if blog_body == '':
            body_error = 'Please enter text for your blog post'
        if not title_error and not body_error:
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?blog_id=" + str(new_blog.id))  
        else:
            return render_template('newpost.html', title_error = title_error, body_error = body_error)   
    return render_template('newpost.html')

@app.route('/blog')
def get_blog():
    blog_id = request.args.get('blog_id')
    if blog_id:
        blog = Blog.query.get(blog_id)
        blogs = None
    else:
        blog = None
        blogs = Blog.query.all() 
    return render_template ('blog.html', blogs=blogs, blog=blog, id=blog_id)

@app.route('/user')
def single_user():
    user_id = request.args.get('user_id')
    if user_id:
        blogs = Blog.query.filter(Blog.owner_id==user_id).all()
    return render_template ('blog.html', blogs=blogs, user_id=user_id)


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()
