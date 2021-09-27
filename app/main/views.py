from flask import render_template,request,redirect,url_for,abort
from . import main
from ..models import User,Blog,Comment, Role
from ..requests import get_quotes
from .. import db,photos
from .forms import UpdateProfile,BlogForm,CommentForm
from flask_login import login_required,current_user
import datetime

@main.route('/')
def index():
    '''
    Function returns the index page and its data
    '''

    title = 'Welcome to GrOti Blog'
    blogs = Blog.query.order_by(Blog.posted.desc()).all()
    quote = get_quotes()
    # get blogs by cateory
    ecom_blog = Blog.get_blogs('e_Commerce')
    ftech_blog = Blog.get_blogs('Future_Tech')
    webdev_blog = Blog.get_blogs('Web_Development')    

  
    return render_template('index.html', title=title, quote=quote, blogs=blogs, e_Commerce=ecom_blog,Future_Tech= ftech_blog,Web_Development=webdev_blog )

@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username = uname).first()
    blogs_count = Blog.count_blogs(uname)
    user_joined =user.date_joined.strftime('%b %d, %Y')

    if user is None:
        abort(404)
    return render_template("profile/profile.html", user = user, blogs = blogs_count, date = user_joined)

@main.route('/user/<uname>/update',methods = ['GET','POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username = uname).first()
    if user is None:
        abort(404)

    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile',uname=user.username))
    return render_template('profile/update.html',form = form)

@main.route('/user/<uname>/update/pic',methods= ['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username = uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile',uname=uname))

@main.route('/blog/new', methods = ['GET','POST'])
@login_required
def new_blog():
    blog_form = BlogForm()
    if blog_form.validate_on_submit():
        title = blog_form.title.data
        blog = blog_form.text.data
        category = blog_form.category.data

        # instance of ana updated blog
        new_blog =Blog(blog_title = title, blog_content= blog, blog_category = category, user = current_user)

        # save new blog post
        new_blog.save_blog()
        return redirect(url_for('.index'))

    title = 'New Blog Post'
    return render_template('new_blog.html', title = title, blog_form = blog_form)

@main.route('/blogs/ecom_blog.html')
def ecom_blog():
    
    blogs = Blog.get_blogs('e-Commerce')

    return render_template("ecom_blog.html", blogs = blogs) 

@main.route('/blogs/ftech_blog.html')
def ftech_blog():

    blogs = Blog.get_blogs('future-tech')

    return render_template("ftech_blog.html", blogs = blogs) 

@main.route('/blogs/webdev_blog.html')
def webdev_blog():
    
    blogs = Blog.get_blogs('web-development')

    return render_template("webdev_blog.html", blogs = blogs) 

@main.route('/blogs/<int:id>', methods = ['GET','POST'])
def blog(id):
    blog = Blog.get_blog(id)
    posted_date = blog.posted.strftime('%b %d, %Y')
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        comment = comment_form.text.data
        new_comment = Comment(comment = comment,user = current_user,blog_id = blog)

        new_comment.save_comment()

    comments = Comment.get_comments(blog)

    return render_template("blog.html", blog = blog, comment_form = comment_form, comments = comments, date = posted_date)   


@main.route('/user/<uname>/blogs')
def user_blogs(uname):
    user = User.query.filter_by(username=uname).first()
    blogs = Blog.query.filter_by(user_id = user.id).all()
    blogs_count = Blog.count_blogs(uname)
    user_joined = user.date_joined.strftime('%b %d, %Y')

    return render_template("profile/blogs.html", user=user,blogs=blogs,blogs_count=blogs_count,date = user_joined)









