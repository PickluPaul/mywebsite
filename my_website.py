from flask import Flask,render_template,request
import requests
import logging
import pytz
from occasions import occasion
import datetime
from datetime import date, timedelta
from tzwhere import tzwhere
from parameter_store import *

log_file='/var/log/mywebsite.log'
logging.basicConfig(filename=log_file,format='%(asctime)s-%(message)s', level=logging.INFO)
app = Flask(__name__)
YEAR='2019'
counter=0

def get_location(ip):
	url=ipstack_url+'/'+ip+'?access_key='+ipstack_access_key
	try:
		resp=requests.get(url)
		data=resp.json()
		city=data['city']
		country_code=data['country_code']
		latitude=data['latitude']
		longitude=data['longitude']
	except Exception as e:
		logging.error('got below error:')
		logging.error(e)
		city='Bengaluru'
		country_code='IN'
		latitude='12.9833'
		longitude='77.5833'
	return city,country_code,latitude,longitude

def get_time_date(latitude,longitude):
	tz = tzwhere.tzwhere()
	timezone_str = tz.tzNameAt(float(latitude),float(longitude))
	zone = pytz.timezone(timezone_str)
	now = datetime.datetime.now(zone)
	hour=now.strftime("%H")
	date=now.strftime("%d")
	month=now.strftime("%B")[:3]
	month_num=now.strftime("%m")
	return hour,date,month,month_num

def get_wishing(hour):
	if int(hour)<12:
		wishing='Good Morning'
	elif int(hour)>=12 and int(hour)<=16:
		wishing='Good Afternoon'
	else:
		wishing='Good Evening'
	return wishing

def get_greeting(date,month):
	day=date+' '+month
	if day in occasion.keys():
		greeting='Happy '+occasion[day]
	else:
		greeting='Namaste!!!'
	return greeting


def get_weather(city):
	url=apixu_url+city
	try:
		resp=requests.get(url)
		data=resp.json()
		temp=data['current']['temp_c']
		max_temp=data['forecast'][u'forecastday'][0]['day']['maxtemp_c']
		min_temp=data['forecast'][u'forecastday'][0]['day']['mintemp_c']
		forcast=data['forecast'][u'forecastday'][0]['day']['condition']['text']
	except Exception as e:
		logging.error('got below error:')
		logging.error(e)
		temp='22'
		max_temp='27'
		min_temp='18'
		forcast='Pleasent'
	return temp,max_temp,min_temp,forcast

def get_news(city,month_num):
	headlines=[]
	day = date.today() - timedelta(1)
	yesterday='{0}-{1}-{2}'.format(YEAR,month_num,day.strftime('%d'))
	url=newsapi_url+city+'&from='+yesterday
	logging.error(url)
	try:
		resp=requests.get(url)
		data=resp.json()
		logging.error(data)
		for x in range(0,5):
			headlines.append('. '+data['articles'][x]['title']+'.')
	except Exception as e:
		logging.error('got below error:')
		logging.error(e)
		headlines.append('No furthur news received on this.')
	return headlines

@app.route('/')
def welcome():
	global counter
	counter=counter+1
	
	ip=request.remote_addr
	if str(ip)=='127.0.0.1':
		ip='122.167.29.17'
	
	logging.critical('[{0}]Total number of visit: {1}'.format(ip,counter))
	city,country_code,latitude,longitude=get_location(ip)
	hour,date,month,month_num=get_time_date(latitude,longitude)
	wishing=get_wishing(hour)
	greeting=get_greeting(date,month)
	temp,max_temp,min_temp,forcast=get_weather(city)
	headlines=get_news(city,month_num)
	welcome_msg=wishing+' and '+greeting
	return render_template('welcome.html',welcome_msg=welcome_msg,city=city,temp=temp,max_temp=max_temp,min_temp=min_temp,forcast=forcast,headlines=headlines)

@app.route('/profile')
def profile():
	return render_template('profile.html',greeting="Namaste!!!")


@app.route('/submit', methods=['POST','GET'])
def submit():
	logging.critical('Message Received: From={0} email={1} Message={2}'.format(request.form['Name'],request.form['_replyto'],request.form['message']))
	return render_template('thankyou.html')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)
