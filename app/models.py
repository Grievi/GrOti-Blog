from flask.globals import current_app
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from . import login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin,db.Model):
    
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(55),index =True)
    firstname = db.Column(db.String(255))
    lastname = db.Column(db.String(255))
    bio=db.Column(db.String)
    email = db.Column(db.String(55),unique = True,index = True)
    pass_secure = db.Column(db.String(55))
    date_joined = db.Column(db.DateTime,default=datetime.utcnow)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

# no relationship yet
    def __init__(self,**kw):
    
        super(User,self).__init__(**kw)
        #  assign the administrator role 
        if self.role is None and self.email == current_app.config['FLASKY_ADMIN']:
            self.role = Role.query.filter_by(name="ADMIN").first()

        #  if a user's role does not exist 
        if self.role is None:
            #  assign a default role 
            self.role = Role.query.filter_by(default=True).first()
    
    #  determining user roles 
    def can(self,perm):
        return self.role is not None and self.role.has_permission(perm) 
    
    def is_administrator(self):
        return self.can(Permission.ADMIN)
 
    @property
    def password(self):
        raise AttributeError("password is not readable attribute")
    
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f'User {self.username}'


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(10))
    default = db.Column(db.Boolean, default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User',backref='role',lazy='dynamic')

    def __init__(self,**kw):
        super(Role,self).__init__(**kw)
        if self.permissions is None:
            self.permissions = 0

    #  determine if there are permissions 
    def has_permission(self,perm):
        return self.permissions & perm == perm

    #  add permissions 
    def add_permission(self,perm):
        if not self.has_permission(perm):
            self.permissions += perm

    #  remove permissions 
    def remove_permission(self,perm):
        if self.has_permission(perm):
            self.permissions -= perm

    #  reset the permissions 
    def reset_permission(self):
        self.permissions = 0   
    
    # insert a role
    @staticmethod
    def insert_roles():
        roles={
           "User":[
                Permission.FOLLOW,
                Permission.COMMENT,
            ],
            
            "ADMIN":[
                Permission.FOLLOW,
                Permission.COMMENT,
                Permission.ADMIN,          
            ] 
        }
        default_role='User'
        for r in roles:
            #  search for two roles that exist in the database table 
            role = Role.query.filter_by(name=r).first()
            #  if there is no such role, add it immediately ， convenient for future expansion 
            if role is None:
                role = Role(name=r)
            
            #  reset the permissions 
            role.reset_permission()
            for perm in roles[r]:
                #  add the permissions one by one 
                role.add_permission(perm)
            
            #  writes the default user to the database 
            role.default = (role.name == default_role)
            db.session.add(role)
        
        db.session.commit()

class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer,primary_key = True)
    blog_title = db.Column(db.String)
    category = db.Column(db.String)
    blog_content = db.Column(db.String)
    posted = db.Column(db.DateTime,default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    comments = db.relationship('Comment',backref = 'pitch_id',lazy = "dynamic")

    def save_blog(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_blogs(cls,category):
        blogs = Blog.query.filter_by(category=category).all()
        return blogs

    @classmethod
    def get_blog(cls,id):
        blog = Blog.query.filter_by(id=id).all()
        return blog

    @classmethod
    def count_blogs(cls,uname):
        user = User.query.filter_by(username=uname).first()
        blogs = Blog.query.filter_by(user_id=user.id).all()

        blogs_count = 0
        for blog in blogs:
            blogs_count += 1

        return blogs_count

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer,primary_key = True)
    comment = db.Column(db.String(1200))
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    posted = db.Column(db.DateTime,default=datetime.utcnow)
    blog = db.Column(db.Integer,db.ForeignKey("blogs.id"))

    def save_comment(self):
        db.session.add(self)
        db.session.commit()

    # def delete(self):
    #     db.session.remove(self)
    #     db.session.commit()

    @classmethod
    def get_comments(cls,pitch):
        comments = Comment.query.filter_by(pitch_id=pitch).all()
        return comments

# Set up permission for different users
class Permission:
    FOLLOW=1
    COMMENT=2
    ADMIN=3


