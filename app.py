from flask import Flask,render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField
from passlib.hash import sha256_crypt
from fuzzywuzzy import fuzz
from better_profanity import profanity

app= Flask(__name__)

#config MySQL
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='prajna'
app.config['MYSQL_PASSWORD']='prajnabhat077'
app.config['MYSQL_DB']='duplicatecommentdetector'
app.config['MYSQL_CURSORCLASS']='DictCursor'
#initialize
mysql=MySQL(app)

@app.route('/')
def index():
	cur=mysql.connection.cursor()
	result = cur.execute("SELECT * FROM quiz")
	questions = cur.fetchall()
	if result>0:
		return render_template('home.html', questions=questions)
	else:
		msg="no questions in the database"
		return render_template('aboutus.html', msg=msg)
	cur.close()

@app.route('/about')
def about():
	return render_template('aboutus.html')

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/signup')
def signup():
	return render_template('signup.html')

@app.route('/question_page')
def question_page():
	q_id = request.args['qid']
	cur=mysql.connection.cursor()
	result = cur.execute("SELECT * FROM quiz where qid=%s",[q_id])
	question = cur.fetchone()
	prev_ans = cur.execute("SELECT * FROM answers where qid=%s",[q_id])
	panswers = cur.fetchall()
	if result>0:
		return render_template('question_page.html',question=question,panswers=panswers)
	else:
		msg="no questions in the database"
		return render_template('error.html', msg=msg)
	cur.close()

class Ques_msg(Form):
	user2 = StringField('user2')
	q=StringField('q')
	a=StringField('option1')
	b=StringField('option2')
	c=StringField('option3')
	d=StringField('option4')

@app.route('/asked_questions', methods=['GET','POST'])
def asked_questions():
	form = Ques_msg(request.form)
	user2 = form.user2.data
	app.logger.info(user2)
	if(user2=="" or user2==None):
	   return render_template('login.html')
	q = form.q.data
	app.logger.info(q)
	cur=mysql.connection.cursor()
	ress = cur.execute("select * from quiz where ques=%s",[q])
	app.logger.info(q," this ",ress)
	if(ress>=1):
		return render_template('message.html',mesage="Hey this question is already posted you can check it in the home tab...")
	a = form.a.data
	b = form.b.data
	c = form.c.data
	d = form.d.data
	cur=mysql.connection.cursor()
	try:
		cur.execute("Insert into quiz(qid,ques,a,b,c,d) values(%s,%s,%s,%s,%s,%s)",(None,q,a,b,c,d))
		mysql.connection.commit()
	except TypeError as e:
		app.logger.info(e)
		return
	cur.close()
	return render_template('message.html',mesage="Thanks for putting up your question here!")

@app.route('/questions')
def questions():
	return render_template('questions.html')

def convert(lst):
    return ([i for item in lst for i in item.split()])

class Message(Form):
	ans=StringField('ans')
	id1=StringField('id1')
	user=StringField('user')

@app.route('/message', methods=['GET','POST'])
def message():
	no_p=""
	count=0
	punc ='''!()-[]{};:'"\,<>./?@#$%^&*_~'''
	conj = ['and','the','an','but','is','are','in','for','to','so','of']
	form = Message(request.form)
	user = form.user.data
	id1=form.id1.data
	app.logger.info(user)
	if(user=="" or user==None):
	   return render_template('login.html')
	mes = ""
	if request.method =='POST':
		app.logger.info(id1)
		ans=form.ans.data
		if(profanity.contains_profanity(ans)):
			return render_template('message.html',mesage="Be nicer and don't use such offensive language!")
		for char in ans:
			if char not in punc:
				no_p = no_p + char
		cur=mysql.connection.cursor()
		resu = cur.execute("SELECT * FROM answers WHERE qid= %s", [id1])
		if resu == 1:
			app.logger.info("inside resu=1")
			dat = cur.fetchone()
			lisdat = dat["answers"]
			c = fuzz.token_set_ratio(lisdat,no_p)
			#d = fuzz.token_set_ratio(listat,)
			app.logger.info(c)
			if c>=50:
				mes="Sorry... someone has already posted this answer. Try answering some other question!"
			else:
				mes = "YaaY! your answer has been recorded. Thank you for taking time and helping geeks struggling with this question. Don't stop keep answering.!"
				cur.execute("INSERT INTO answers(a_id,answers,qid,email) VALUES(%s,%s,%s,%s)",(None,ans,id1,user))
				mysql.connection.commit()
		elif resu>1:
			app.logger.info("inside resu>1")
			dat = cur.fetchall()
			for row in dat:
				dno_p=""
				dli = row["answers"]
				for char in dli:
					if char not in punc:
						dno_p = dno_p + char
				m= fuzz.token_set_ratio(no_p,dno_p)
				app.logger.info(m)
				if m >=70:
					count+=1
			if count>0:
				mes="Sorry... someone has already posted this answer. Try answering some other question!"
			else:
				mes = "YaaY! your answer has been recorded. Thank you for taking time and helping geeks struggling with this question. Don't stop keep answering.!"
				cur.execute("INSERT INTO answers(a_id,answers,qid,email) VALUES(%s,%s,%s,%s)",(None,ans,id1,user))
				mysql.connection.commit()
		else:
			cur.execute("INSERT INTO answers(a_id,answers,qid,email) VALUES(%s,%s,%s,%s)",(None,ans,id1,user))
			mysql.connection.commit()
		cur.close()
		return render_template('message.html',mesage=mes)
	return render_template('question_page.html')


if __name__=='__main__':
	app.secret_key='secret123'
	app.run(debug=True)
