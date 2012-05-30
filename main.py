import os
import cgi
import datetime
import webapp2
import csv
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template


header ='''<!DOCTYPE HTML><html><head>
<meta charset="UTF-8">
<title>School Announcements</title>
<link href="/styles/jquery.mobile-1.0b3.min.css" rel="stylesheet" type="text/css" />
<script src="/styles/jquery-1.6.4.min.js" type="text/javascript"></script>
<script type="text/javascript">
	$(document).bind("mobileinit", function() { 
		$.mobile.page.prototype.options.addBackBtn = true; 
	}); 
</script>
<script src="/styles/jquery.mobile-1.0b3.min.js" type="text/javascript"></script>
<link href="/styles/custom.css" rel="stylesheet" type="text/css" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
</head><body><center><div data-theme="e">'''

footer = '''<div data-role="footer" data-theme="e">
			<h4>&copy;Moof 2012</h4>
	</div></center></body></html>'''

class Greeting(db.Expando):
	''' defining database '''
	# author = db.StringProperty(required=True)
	title = db.StringProperty(required=True)
	content = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)



class MainPage(webapp2.RequestHandler):
	def get(self):
		
		user=users.get_current_user()
		query=Greeting.gql('WHERE pid= :1', user.nickname())
		result=query.fetch(1)
		self.response.out.write(result)
		guestbook_name = self.request.get('guestbook_name')
		
		
		greetings = db.GqlQuery("SELECT * "
								"FROM Greeting "
								"ORDER BY date DESC LIMIT 10")
		
		if user:
			self.response.out.write(header+ '''<div data-role="header" data-theme="e" data-backbtn="false">
    <align="left"><h1>DHS Announcements</h1><h5>Welcome, %s! Not you? <a href=%s >Logout</a></align></h5><br /></body></html>
  </div>''' % (str(user.nickname()), users.create_logout_url(self.request.uri)))
  
		else:
			self.response.out.write(header + '''You need to <a href=%s >Login</a></body></html>'''%(users.create_login_url(self.request.uri)))
		
		list = csv.reader(open("teacherlist.csv","rb"), delimiter=',')
		for row in list:
			if row[2]==user.email()[:-7]:
				self.response.out.write(header + ''' <div data-theme="e">
				<h3>Post an Announcement!</h3>
						<form action="/post" method="post">
								<div>Title: <textarea name="title" rows="1" cols"60"></textarea></div>
								<div>Details: <textarea name="content" rows="3" cols="60"></textarea></div>
								<div><input type="submit" value="Post Announcement"></div>
							</form></div>
					</body></html>
							''')
				break
					

		for greeting in greetings:
			
			if users.get_current_user().nickname():
				self.response.out.write('''(<b>%s</b>)'''%users.get_current_user())
				self.response.out.write('''<br /><b>%s</b>:'''%greeting.title)
			else:
				self.response.out.write('''%s wrote:'''%users.get_current_user().nickname())
			self.response.out.write('''<blockquote>%s</blockquote>'''%cgi.escape(greeting.content))
		
			self.response.out.write('''<h3><b>%s</b></h3>'''%str(greeting.title))
			# self.response.out.write('''<h4> - %s</h4>'''%str(greeting.author))
			self.response.out.write('''<p>%s</p>'''%(str(greeting.content)))
		self.response.out.write(footer)


		

class Announcements(webapp2.RequestHandler):
	def post(self):
		greeting = Greeting()
		user=users.get_current_user().nickname()
		query=Greeting.gql('WHERE pid= :1', user.nickname())
		result=query.fetch(1)
		greeting=result[0]
		list=csv.reader(open("teacherlist.csv","rb"), delimiter=',')
		for row in list:
			if row[2]==user:
				greeting.author= row[0]+' '+row[1]

				break
			
		greeting.content = self.request.get('content')
		greeting.title = self.request.get('title')
		greeting.put()
		self.redirect('/')
		


# main
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/post', Announcements)
], debug=True)
# g = Greeting(author="%s"%greeting.author,title="%s"%greeting.title,content="%s"%greeting.content)
# g.put()