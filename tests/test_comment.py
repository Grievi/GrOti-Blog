from app.models import Comment,User,Blog
from app import db
import unittest

class CommentModelTest(unittest.TestCase):
    def setUp(self):
        self.user_Grievin = User(username = 'Grievin',password = 'potato', email = 'grievin@ms.com')
        self.new_blog = Blog(id=1,blog_title='Test',blog_content='This is a test blog',category="webdev",user = self.user_Grievin)
        self.new_comment = Comment(id=1,comment='Test comment',user=self.user_Grievin,Blog=self.new_blog)

    def tearDown(self):
        Blog.query.delete()
        User.query.delete()

    def test_check_instance_variables(self):
        self.assertEquals(self.new_comment.comment,'Test comment')
        self.assertEquals(self.new_comment.user,self.user_Grievin)
        self.assertEquals(self.new_comment.blog,self.new_blog)