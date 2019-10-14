import pytz
import random
import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, request, render_template
from td.db.models import Tradable, Option, OptionData, session


app = Flask(__name__, template_folder="static/templates")

@app.route('/')
def index():
    ''' Home Page Endpoint
    '''
    # Get the amount of memory used for display:
    gigabytes = memoryused()

    tradables = session.query(Tradable).filter_by(enabled=True).all()
    spy = session.query(Tradable).filter_by(name='SPY').all()
    tradables += spy
    tradables.sort(key=lambda x: x.name)
    return render_template('index.html', tradables=tradables, gigabytes=gigabytes)

@app.route('/tradable/<int:id>')
def tradable(id):
    '''
    '''
    timestamp = request.args.get('timestamp')

    tradable = session.query(Tradable).get(id)
    data, fetchtime = getchain(tradable.name, timestamp=timestamp)
    dates = getdates(tradable.name)
    return render_template('tradable.html',
        tradable=tradable,
        data=data,
        fetchtime=fetchtime,
        dates=dates,
    )

@app.route('/tradable/option/<int:id>')
def option(id):
    value = session.query(OptionData).get(id)
    return render_template('option.html', value=value)

def memoryused():
    ''' Get's the amount of memory used in GB
    '''
    query = session.execute("SELECT pg_database_size('options');")
    memory = [byts for (byts,) in query][0]
    gigabytes = memory / (1000. ** 3)
    return round(gigabytes, 2)

def getdates(name='SPY'):
    ''' Get a list of the data snapshots for the given tradable
    '''
    tradable = session.query(Tradable).filter_by(name=name).first()
    query = session.execute("SELECT id FROM options WHERE tradable_id=%s;" % tradable.id)
    optionids = [str(id) for (id,) in query]

    # Get the Time of The Most Recent Options Data Query For this Tradable:
    query = session.execute("SELECT time, count(*) FROM options_data WHERE option_id IN (%s) GROUP BY time;" % ', '.join(optionids))
    dates = [date for (date, count) in query if count > 1]
    dates.sort(reverse=True)
    return dates

def getchain(name='SPY', timestamp=None):
    ''' Get the most recent options chain for the given tradable
    '''
    tradable = session.query(Tradable).filter_by(name=name).first()

    # Get All Option IDs for this Tradable:
    print('Fetching %s Options...' % tradable.name)
    query = session.execute("SELECT id FROM options WHERE tradable_id=%s;" % tradable.id)
    optionids = [str(id) for (id,) in query]

    if not timestamp:
        # Get the Time of The Most Recent Options Data Query For this Tradable:
        print('Determining Most Recent Fetch Time...')
        query = session.execute("SELECT MAX(time) FROM options_data WHERE option_id IN (%s);" % ', '.join(optionids))
        timestamp = list(query)[0][0]
        print('Most recent Fetch Was: %s' % timestamp)
    else:
        # Adjust from Central:
        timestamp += relativedelta(hours=5)
        print('Requested: %s' % timestamp)

    # Get the options data ids for the most recent fetch:
    print('Fetching Most Recent Fetch Options Data IDs...')
    query = session.execute("SELECT id FROM options_data WHERE time='%s';" % str(timestamp))
    dataids = [int(id) for (id,) in query]

    # Get all the options Values:
    print('Collecting Options Data Records From Most Recent API Fetch...')
    values = session.query(OptionData).filter(OptionData.id.in_(dataids)).all()

    timestamp -= relativedelta(hours=5)
    fetchtime = timestamp.strftime('%B %d at %I:%M Central')

    # values = random.sample(values, 1000)
    values.sort(key=lambda item: (item.dte, item.option.type, item.option.strike))
    return values, fetchtime


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
