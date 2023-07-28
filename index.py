from flask import Flask, request, Response, redirect, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import jinja2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
# postgres://prettyprinted_render_example_rywg_user:HXPz0klfGa8Nk0afze0ixiqmlwoW1gxL@dpg-cj23hrc07spkp630flog-a.oregon-postgres.render.com/prettyprinted_render_example_rywg
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    subject = db.Column(db.String(100), unique = True)
    content = db.Column(db.Text, unique = True)
    created = db.Column(db.DateTime, default = datetime.utcnow)

@app.route("/blog")  
def main_page():
    t = jinja_env.get_template("blog.html")
    posts = Post.query.order_by(Post.created.desc()).all()
    if len(posts) > 10:
        posts = posts[0:10]
    return t.render(posts=posts)

@app.route("/blog/<int:id>")
def permalink(id):
    t = jinja_env.get_template("permalink.html")
    posts = Post.query.order_by(Post.created).all()
    posts_id = []
    for post in posts:
        posts_id.append(post.id)
    if id in posts_id:
        posts = posts[id - 1]
        return t.render(posts=posts)
    return abort(404)

@app.route("/blog/newpost", methods=['GET', 'POST'])
def new_post():
    t = jinja_env.get_template("newpost.html")
    if request.method == 'POST':
        subject = request.form["subject"]
        content = request.form["content"]
        if subject and content:
            posts = Post(subject=subject, content=content)
            db.session.add(posts)
            db.session.commit()
            post_id = str(posts.id)
            return redirect("/blog/" + post_id)
        else:
            error = "We need both a subject and blog"
            return t.render(error=error, subject=subject, content=content) 
    return t.render()

if __name__ == "__main__":
    app.run()