from flask import Flask,render_template,request
import logging
import pytz
from occasions import occasion
import datetime

log_file='/var/log/mywebsite.log'
logging.basicConfig(filename=log_file,format='%(asctime)s-%(message)s', level=logging.CRITICAL)
app = Flask(__name__)
ist = pytz.timezone('Asia/Calcutta')
counter=0

@app.route('/')
def index():
	global counter
	counter=counter+1
	logging.critical('No of visit: {0}'.format(counter))
	now = datetime.datetime.now(ist)
	date=now.strftime("%d")
	month=now.strftime("%B")[:3]
	day=date+' '+month
	if day in occasion.keys():
		greeting='Happy '+occasion[day]
	else:
		greeting='Namaste!!!'
	print request.remote_addr
	return render_template('index.html',greeting=greeting)


@app.route('/submit', methods=['POST','GET'])
def submit():
	logging.critical('Message Received: From={0} email={1} Message={2}'.format(request.form['Name'],request.form['_replyto'],request.form['message']))
	return render_template('thankyou.html')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)
