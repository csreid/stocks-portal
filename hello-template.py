from flask import Flask, render_template, request
import datetime
import MySQLdb
import json
import collections

app=Flask(__name__)
db = MySQLdb.connect("localhost", "root", "", "stock_data")
cursor = db.cursor()

@app.route("/")
def index():
	now = datetime.datetime.now()
	timeString = now.strftime("%Y-%m-%d %I:%M:%S")
	templateData={
		'title': 'Hello!',
		'time': timeString,
	}

	return render_template('main.html', **templateData)

@app.route("/quoteCount")
def getCount():
	cursor.execute("select count(*) from quotes limit 10")
	count = cursor.fetchone()[0]
	return '{"count": ' + str(count) + '}'

@app.route("/mostRecent")
def mostRecent():
	limit = request.args.get('count')
	cursor.execute("""
		select symbol, price, timestamp 
		from quotes
		order by timestamp desc
		limit %i
	""" % int(limit))
	results = cursor.fetchall()
	rowarray_list = []
	for row in results:
		t = (row[0], row[1], row[2].strftime("%Y-%m-%d %H:%M:%S"))
		rowarray_list.append(t)
	j = json.dumps(rowarray_list)
	return j

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80, debug=True)
