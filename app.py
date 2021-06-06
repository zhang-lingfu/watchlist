import os
import click

from flask import Flask,render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path,'data.db')
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))

class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（请在命令行窗口查看输出的 URL）：
    print(url_for('hello')) # 输出：/
    # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
    print(url_for('user_page', name='greyli'))
    # 输出：/user/greyli
    print(url_for('user_page', name='peter'))
    # 输出：/user/peter
    print(url_for('test_url_for')) # 输出：/test
    # 下面这个调用传入了多余的关键字参数，
    # 它们会被作为查询字符串附加到 URL 后面。
    print(url_for('test_url_for', num=2))
    # 输出：/test?num=2
    return 'Test page'

@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    name = '催档'
    movies = [
        {'title':'TOAW4催档','year':'0'},
        {'title':'TOAW4战报','year':'1'},
        {'title': 'TOAW4讨论', 'year': '2'},
        {'title': '其他催档', 'year': '3'},
        {'title': '其他战报', 'year': '4'},
        {'title': '其他讨论', 'year': '5'},
        {'title': '试验1', 'year': '6'},
        {'title': '试验2', 'year': '7'},
        {'title': '试验3', 'year': '8'},
        {'title': '试验4', 'year': '9'},
    ]

    user=User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')

@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.route('/0',methods=['GET','POST'])
def toaw4_0():
    return render_template('toaw4_0.html')

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))
        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))
    app.secret_key = 'dev'
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html',user=user,movies=movies)

@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])

def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) >60:
            flash('Invalid input.')
            return redirect(url_for('edit',movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html',movie=movie)

@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))

@app.cli.command()
@click.option('--drop',is_flag=True,help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')