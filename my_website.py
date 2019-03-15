from flask import Flask,render_template,request
import requests
import logging
import pytz
from occasions import occasion
import datetime
from datetime import date, timedelta
from parameter_store import *

log_file='/var/log/mywebsite.log'
logging.basicConfig(filename=log_file,format='%(asctime)s-%(message)s', level=logging.WARNING)
app = Flask(__name__)
count=0
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
	if not city:
		city='Bengaluru'
		country_code='IN'
		latitude='12.9833'
		longitude='77.5833'
	return city.encode('utf-8'),country_code.encode('utf-8'),str(latitude),str(longitude)

def get_time_date(time_date):
	date=time_date.split(' ')[0]
	time=time_date.split(' ')[1]
	year=date.split('-')[0]
	month=date.split('-')[1]
	day=date.split('-')[2]
	hour=time.split(':')[0]
	month_name='Mar'
	return year,month,day,hour,month_name

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


def get_city_details(city):
	url=apixu_url+city
	try:
		resp=requests.get(url)
		data=resp.json()
		temp=data['current']['temp_c']
		max_temp=data['forecast'][u'forecastday'][0]['day']['maxtemp_c']
		min_temp=data['forecast'][u'forecastday'][0]['day']['mintemp_c']
		forcast=data['forecast'][u'forecastday'][0]['day']['condition']['text']
		time_date=data['location']['localtime']
	except Exception as e:
		logging.error('got below error:')
		logging.error(e)
		temp='22'
		max_temp='27'
		min_temp='18'
		forcast='Pleasent'
		time_date='2019-03-15 15:53'
	return temp,max_temp,min_temp,forcast,time_date

def get_news(city,month_num,year):
	headlines=[]
	day = date.today() - timedelta(1)
	yesterday='{0}-{1}-{2}'.format(year,month_num,day.strftime('%d'))
	url=newsapi_url+city+'&from='+yesterday
	try:
		resp=requests.get(url)
		data=resp.json()
		for x in range(0,5):
			headlines.append('. '+data['articles'][x]['title']+'.')
	except Exception as e:
		logging.error('got below error:')
		logging.error(e)
		headlines.append('No furthur news received on this.')
	return headlines

@app.route('/')
def welcome():
        global count
        count=count+1
	ip=request.remote_addr
	city,country_code,latitude,longitude=get_location(ip)
	temp,max_temp,min_temp,forcast,time_date=get_city_details(city)
	year,month,day,hour,month_name=get_time_date(time_date)
	wishing=get_wishing(hour)
	greeting=get_greeting(day,month)
	headlines=get_news(city,month_name,year)
	welcome_msg=wishing+' and '+greeting
        logging.warning('A person visited from %s'%city)
        logging.warning('Total number of visit: %s'%count)
	return render_template('welcome.html',welcome_msg=welcome_msg,city=city,temp=temp,max_temp=max_temp,min_temp=min_temp,forcast=forcast,headlines=headlines)

@app.route('/profile')
def profile():
	return render_template('profile.html',greeting="Namaste!!!")


@app.route('/submit', methods=['POST','GET'])
def submit():
	logging.critical('Message Received: From={0} email={1} Message={2}'.format(request.form['Name'],request.form['_replyto'],request.form['message']))
	return render_template('thankyou.html')


if __name__ == '__main__':
    app.run(threaded=True,debug=True,host='0.0.0.0',port=80)

