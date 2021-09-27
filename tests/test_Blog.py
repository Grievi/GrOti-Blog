from app.models import Comment,User,Blog
from app import db
import unittest

class BlogModelTest(unittest.TestCase):
    def setUp(self):
        self.user_Grievin = User(username = 'Grievin',password = 'access', email = 'grievin@ms.com')
        self.new_blog = Blog(id=1,blog_title='Test',blog_content='This is a test blog',category="ftech",user = self.user_Grievin,likes=0,dislikes=0)

    def tearDown(self):
        Blog.query.delete()
        User.query.delete()

    def test_check_instance_variables(self):
        self.assertEquals(self.new_blog.blog_title,'Test')
        self.assertEquals(self.new_blog.blog_content,'This is a test blog')
        self.assertEquals(self.new_blog.category,"webdevelopment")
        self.assertEquals(self.new_blog.user,self.user_Grievin)

    def test_save_blog(self):
        self.new_blog.save_blog()
        self.assertTrue(len(Blog.query.all())>0)

    def test_get_blog_by_id(self):
        self.new_blog.save_blog()
        got_blog = Blog.get_blog(1)
        self.assertTrue(got_blog is not None)