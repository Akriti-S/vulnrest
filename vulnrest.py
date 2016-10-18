#!/usr/bin/python
import random
import web
import xml.etree.ElementTree as ET
import requests
# listing of urls 
urls=(
"/list_users","list_users",
'/get_user/(.*)',"get_user",
'/authenticate_1',"authenticate_1",
'/authenticate_2','authenticate_2',
'/money_transfer','money_transfer',
'/upload','file_upload',
'/order','order'
)
tree=ET.parse('/root/vulnrest/user.xml')
root=tree.getroot()
app=web.application(urls,globals())
global gen_token
gen_token=10000000001
print gen_token
def login(username,password):
	auth=0
	for user in root.iter():
			print user.attrib.get('username',None)
			if user.attrib.get('username',None)==username and user.attrib.get('password',None)==password:
				auth=1
	return auth


def token_verify(token):
	success=0
	f=open("/root/vulnrest/token.txt")
	l=[]
	for lines in f:
		l.append(lines.replace('\n',''))
	if token in l:
		success=1
	f.close()
	return success	
class list_users:
	def GET(self):
		'''check for authentication by taking token from header'''
		'''print web.ctx.env.get('Host')'''
		output="["
		for child in root:
			output=output+str( child.attrib)+","
		output=output+"]"
		return output
class get_user:
	def POST(self,user):
		data=web.input()
		print data
		token=str(data.token)
		print token
		a="failure"
		success=token_verify(token)
		for child in root:
			print child.attrib['id']
			if child.attrib['id']== user and success==1:
				a= str(child.attrib)
					
		return a

''' on authentication a server will return hardcoded token assigned to the user in code'''
class authenticate_1:
	def GET(self):
		data=web.input()
		username=data.username
		password=data.password
		auth=0
		id=0
		token=0
		global gen_token
		'''code of authentication'''
		auth=login(username,password)				
		'''code of token generation'''
		if(auth==1):
			token=gen_token+1
			print token
			gen_token=token
			print gen_token
			return token
		else:
			return "error"
		
'''tokens are stored in a file which is unrestricted by the server'''
				
class authenticate_2:
	def GET(self):
		data=web.input()
		username=data.username
		password=data.password
		auth=login(username,password)
		if (auth==1):
			'''opening of file'''
			f=open("/root/vulnrest/token.txt")
			a=[]
			print type(a)
			for line in f:
				a.append(line.strip('/n'))
			print a
			r=random.randint(0,5)
			return a[r]
			f.close()
		else:
			return "error"			
		'''reading of token and assiging one to the user'''
		
'''transfer of money if token is valid'''
class money_transfer:
	''' accept user token in header'''
	def POST(self):
		data=web.input()
		token=data.token
		amount=int(data.amount)
		sender=data.sender
		receiver=data.receiver
		success=token_verify(token)
		for child in root.iter():
			print child
			balance= child.attrib.get("balance",None)
			if child.attrib.get("id",None)==sender:
				child.set("balance",str(int(balance)-amount))
				print child.attrib.get("balance",None)
			if child.attrib.get("id",None)==receiver:
				child.attrib["balance"]=str(int(balance)+amount)
				print child.attrib.get("balance",None)
		tree.write("user.xml")
		return "money transfered"				
	'''fetch amt to be trsansfered from user'''
	'''deduct amt from sender and add to receiver'''

class order:
	def POST(self):
		data=web.input()
		id=data.id
		token=data.token
		pizza=data.pizza
		name=data.name
		success=token_verify(token)
		print type(id)	
		a=""
		print success
		if success:
			print "inside"
			for child in root.iter():
				#print child.attrib.get("id",None)
				id1= child.attrib.get("id",None)
				print type(id1)
				if child.attrib.get("id",None)==str(id):
					print child.attrib.get("id",None)
					a="pizza order placed for", child.attrib.get("name",None)
		else:
			 a="error"
		return a			
'''xxe'''
class file_upload:
	def GET(self):
		web.header("Content-Type","text/html; charset=utf-8")
		return """<html><head></head><body>
		<form method="POST" enctype="multipart/form-data" action="">
		<input type="file" name="myfile"/>
		<br/>
		<input type="submit"/>
		</form>
		</body>
		</html>"""
	def POST(self):
		x=web.input(myfile={})
		filedir='.'
		if 'myfile' in x:
			filepath=x.myfile.filename.replace('\\','/')
			filename=filepath.split('/')[-1] 
            		fout = open(filedir +'/'+ filename,'w') # creates the file where the uploaded file should be stored
            		fout.write(x.myfile.file.read()) # writes the uploaded file to the newly created file.
            		fout.close() # closes the file, upload complete.
        	raise web.seeother('/upload')

if __name__=="__main__":
	app.run()
