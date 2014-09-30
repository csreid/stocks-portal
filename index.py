from flask import Flask, render_template, request
import datetime
import MySQLdb
import json
import collections

app=Flask(__name__)

@app.route("/")
def index():
	now = datetime.datetime.now()
	timeString = now.strftime("%Y-%m-%d")
	templateData={
		'title': 'Stock price DB',
		'time': timeString,
	}

	return render_template('main.html', **templateData)

@app.route("/company")
def company():
	db = MySQLdb.connect("localhost", "root", "", "stock_data")
	cursor = db.cursor()
	symbol=request.args.get('symbol')
	now = datetime.datetime.now()
	timeString = now.strftime("%Y-%m-%d")
	cursor.execute("""
			select symbol, name, exchange
			from companies
			where symbol='%s'
	""" % symbol)
	row = cursor.fetchone()
	
	templateData={
			'title': "Company View",
			'symbol': symbol,
			'name': row[1],
			'exchange': row[2],
			'time':timeString
	}
	return render_template('company.html', **templateData)


@app.route("/companies")
def companies():
		db = MySQLdb.connect("localhost", "root", "", "stock_data")
		cursor = db.cursor()
		now = datetime.datetime.now()
		timeString = now.strftime("%Y-%m-%d")
		templateData={
				'title': 'Companies',
				'time': timeString
		}
		return render_template('companies.html', **templateData)

@app.route("/quoteCount")
def getCount():
	db = MySQLdb.connect("localhost", "root", "", "stock_data")
	cursor = db.cursor()
	cursor.execute("select count(*) from quotes limit 10")
	count = cursor.fetchone()[0]
	return '{"count": ' + str(count) + '}'

@app.route("/mostRecent")
def mostRecent():
	db = MySQLdb.connect("localhost", "root", "", "stock_data")
	cursor = db.cursor()
	limit = request.args.get('count')
	cursor.execute("""
		select symbol, price, timestamp 
		from quotes
		order by timestamp desc
		limit %i
	""" % int(limit))
	results = cursor.fetchall()
	rowarray_list = []
	for row in reversed(results):
		t = (row[0], row[1], row[2].strftime("%Y-%m-%d %H:%M"))
		rowarray_list.append(t)
	j = json.dumps(rowarray_list)
	return j

@app.route("/getCompanies")
def getCompanies():
		db = MySQLdb.connect("localhost", "root", "", "stock_data")
		cursor = db.cursor()
		cursor.execute("""
				select name, symbol, exchange
				from companies
		""")
		results = cursor.fetchall()
		rowarray_list = []
		for row in results:
				t = (row[0], row[1], row[2])
				rowarray_list.append(t)
		j = json.dumps(rowarray_list)
		return j

@app.route("/getCompanyBySymbol")
def getCompanyBySymbol():
		db = MySQLdb.connect("localhost", "root", "", "stock_data")
		cursor = db.cursor()
		name = request.args.get('symbol')
		cursor.execute("""
				select *
				from companies
				where symbol = '%s'
		""" % name)
		result = cursor.fetchone()
		dictResult = {"id": result[0], "symbol": result[1], "name": result[2], "exchange":result[3]}
		j = json.dumps(dictResult)
		return j

@app.route("/getQuotesBySymbol")
def getQuotesBySymbol():
	db = MySQLdb.connect("localhost", "root", "", "stock_data")
	cursor = db.cursor()
	symbol = request.args.get('symbol')
	num = request.args.get('num')
	cursor.execute("""select timestamp, price from quotes, companies where quotes.symbol=companies.id and companies.symbol='{0}' order by timestamp desc limit {1}""".format(symbol, num))
	results = cursor.fetchall()
	data = []
	labels = []
	for row in results:
		labels.append(row[0].strftime("%Y-%m-%d %H:%M:%S"))
		data.append(row[1])
	datasets1 = {}
	datasets1['labels'] = labels
	datasets1['datasets']=[data]
	datasets1['label'] = "Test"
	datasets1['fillColor'] = "rgba(220,220,220,0.2)"
	datasets1['strokeColor'] = "rgba(0,0,0, 1)"
	datasets1['pointColor'] = "rgba(0,0,0, 1)"
	datasets1['pointStrokeColor'] = "#fff"
	datasets1['pointHighlightFill'] = "#fff"
	datasets1['pointHighlightFillStroke'] = "rgba(220, 220, 220, 1"
	datasets1['data']=data

	datasets = [datasets1]

	toReturn = {}
	toReturn['labels']=labels
	toReturn['datasets']=datasets

	j = json.dumps(toReturn)
	
	return j

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80, debug=True)
