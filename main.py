import threading
import datetime as dt
from datetime import timezone, timedelta
from dateutil.relativedelta import relativedelta, FR

from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from market_dicts import title_dict
from models import app, db, tables, ohlc_tables, tnames, cps
from high_charts_builder import HCBuilder
from bokeh_plots_builder import BPBuilder

hc_builder = HCBuilder(tables, ohlc_tables, db)
bp_builder = BPBuilder(tables, ohlc_tables, db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream-highcharts', methods=["GET","POST"])
def stream_highcharts():
    return render_template('highcharts.html', currency_pairs=cps)

@app.route('/stream-bokeh')
def stream_bokeh():
    is_closed = closed(dt.datetime.now(tz=timezone.utc))
    script, divs = bp_builder.build_components(is_closed)
    return render_template('bokeh.html', divs=divs, script=script, currency_pairs=cps, is_closed=is_closed)

@app.route('/ohlc-highcharts')
def ohlc_highcharts():
    return render_template('ohlc_highcharts.html', currency_pairs=cps)

@app.route('/ohlc-bokeh')
def ohlc_bokeh():
    script, divs = bp_builder.build_ohlc_components()
    return render_template('ohlc_bokeh.html', divs=divs, script=script, currency_pairs=cps)

@app.route('/returns-highcharts')
def returns_highcharts():
    return render_template('returns_highcharts.html', currency_pairs=cps)

@app.route('/returns-bokeh')
def returns_bokeh():
    script, div = bp_builder.build_returns_components()
    return render_template('returns_bokeh.html', div=div, script=script, currency_pairs=cps)

@app.route('/data/<type>', methods=['GET'])
def data(type):
    if type=='returns':
        response = hc_builder.build_returns_response()
        return jsonify(response)
    elif type=='stream-highcharts':
        now = dt.datetime.now(tz=timezone.utc).replace(microsecond=0)
        is_closed = closed(now)
        response = hc_builder.build_response(is_closed)
        return jsonify(response)
    elif type=='ohlc-highcharts':
        now = dt.datetime.now(tz=timezone.utc).replace(microsecond=0)
        is_closed = closed(now)
        response = hc_builder.build_ohlc_response(is_closed)
        return jsonify(response)

@app.route("/data/<tname>/<int:cutoff>", methods=['POST', 'GET'])
def get_data(tname, cutoff):
    table = tnames[tname]
    now = dt.datetime.now(tz=timezone.utc).replace(microsecond=0)
    is_closed = closed(now)
    if is_closed == False:
        n_minutes_ago = dt.datetime.now() - timedelta(minutes=cutoff)
    else:
        cutoff = now.replace(tzinfo=None) + relativedelta(weekday=FR(-1))
        n_minutes_ago =\
        cutoff.replace(hour=14,minute=30,second=0,microsecond=0)
    rows = table.query\
        .filter(table.timestamp > n_minutes_ago)\
        .order_by(table.timestamp)\
        .all()
    timestamps = []
    rates = []
    for row in rows:
        x = row.timestamp.timestamp()*1000
        y = row.rate
        timestamps.append(x)
        rates.append(y)
    return jsonify(timestamp=timestamps, rate=rates)

def closed(now):
	return (
    	(now.weekday() == 4 and now.time() >= dt.time(21,1))\
    	| (now.weekday() == 5) \
    	| (now.weekday() == 6 and now.time() < dt.time(21))
    )
