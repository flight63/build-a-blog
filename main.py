# importing necessary modules + session + flask
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
# importing datetime for bonus in reverse ordering blog posts
from datetime import datetime
from sqlalchemy import desc

app = Flask(__name__)
app.config['DEBUG'] = True

# SQL database configuration: username:password@server:portnumber/databasename
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog123@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# creating blog persistent class
class Blog(db.Model):
    # necessary properties
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    created = db.Column(db.DateTime)
    # initializer or constructor for blog class
    def __init__(self, title, body):
        self.title = title
        self.body = body
        # created date for reverse ordering posts
        self.created = datetime.utcnow()

    def is_valid(self):
        if self.title and self.body and self.created:
            return True
        else:
            return False

@app.route('/')
def index():
    return redirect('/blog')

# route to main blog page
@app.route('/blog')
def blog_index():
    # args getting id dictionary element from table
    blog_id = request.args.get('id')
    blogs = Blog.query.all()

    if blog_id:
        post = Blog.query.get(blog_id)
        blog_title = post.title
        blog_body = post.body
        # Use Case 1: Click on a blog entry's title on the main page and go to a blog's individual entry page.
        return render_template('entry.html', title="Blog Entry #" + blog_id, blog_title=blog_title, blog_body=blog_body)

    # TODO - Sort posts from newest to oldest
    sort = request.args.get('sort')

    if (sort=="newest"):
        blogs = Blog.query.order_by(Blog.created.desc()).all()
    elif (sort=="oldest"):
        blogs = Blog.query.order_by(Blog.created.asc()).all()
    else:
        blogs = Blog.query.all()
    return render_template('blog.html', title="Build A Blog", blogs=blogs)

# handler route to new post page.
@app.route('/post')
def new_post():
    return render_template('post.html', title="Add New Blog Entry")

# handler route to validate post title & body fields
@app.route('/post', methods=['POST'])
def verify_post():
    blog_title = request.form['title']
    blog_body = request.form['body']
    title_error = ''
    body_error = ''

    # error validation messages, if blog/title is empty return error text.
    if blog_title == "":
        title_error = "Title required."
    if blog_body == "":
        body_error = "Content required."

    # add new blog post and commit it to table with new id.
    if not title_error and not body_error:
        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()
        blog = new_blog.id
        # Use Case 2: After adding a new blog post, instead of going back to the main page, we go to that blog post's individual entry page. Redirect to specific blog id page.
        return redirect('/blog?id={0}'.format(blog))
    else:
        # return user to post page with errors.
        return render_template('post.html', title="Add New Blog Entry", blog_title = blog_title, blog_body = blog_body, title_error = title_error, body_error = body_error)

if __name__ == '__main__':
    app.run()