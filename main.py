from flask import Flask, escape, request, session, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:no@localhost:5000/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '333vdfjdo0BIEO0430nfe&*GO^AWAY&^&dfmo2349s'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<blog %r>' % self.name


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '%r' % self.username


@app.before_request
def require_login():
    allowed_routes = ['index', 'blogs', 'login', 'signup']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    username = ''
    username_error = ''
    password_error = ''
    verify_error = ''
    existing_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_in_db = User.query.filter_by(username=username).first()

        # validators
        if username_in_db:
            existing_error = 'It looks like "' + username + '" is taken. Sad day for you.'

        if username == '' or not len(username) > 3 or len(username) > 20:
            username_error = "Its either blank, too short or too long. Figure it out."
            username = ''

        if password == '' or not len(password) > 3 or len(password) > 20:
            password_error = "Its either blank, too short or too long. Figure it out."

        if password != verify:
            password_error = 'They were not the same. Like at all.'

        # if not errors
        if not username_error and not password_error and not verify_error and not existing_error:
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            session['user'] = user.username
            return redirect('/blogs')

    return render_template('register.html', username=username, username_error=username_error, password_error=password_error, verify_error=verify_error, existing_error=existing_error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = ''
    username_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # upon successfull login
        if user and (password == user.password):
            session['user'] = username
            return redirect('/blogs')

        # validators
        if not user or user.password != password:
            username_error = "Try Again. Username or password are wrong"

    return render_template('login.html', username=username, username_error=username_error)

# TODOs fix this
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
            return render_template('newpost.html', title_error=title_error, body_error=body_error)
    return render_template('newpost.html')


@app.route('/blogs')
def blogs():

    blogs = Blog.query.all()

    blog_id = request.args.get('id')
    username = request.args.get('username')

    if blog_id:
        blogs = Blog.query.filter_by(id=blog_id).all()

    if username:
        user = User.query.filter_by(username=username).first()
        blogs = user.blogs

    return render_template('blogs.html', blogs=blogs)


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


if __name__ == '__main__':
    app.run()