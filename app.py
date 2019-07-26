import random
import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template
from .td.db.models import Tradable, Option, OptionData, session


app = Flask(__name__, template_folder="static/templates")

@app.route('/')
def index():
    tradables = session.query(Tradable).filter_by(enabled=True).all()
    spy = session.query(Tradable).filter_by(name='SPY').all()
    tradables += spy
    tradables.sort(key=lambda x: x.name)
    return render_template('index.html', tradables=tradables)

@app.route('/tradable/<int:id>')
def tradable(id):
    tradable = session.query(Tradable).get(id)
    data, fetchtime = getchain(tradable.name)
    return render_template('tradable.html', tradable=tradable, data=data, fetchtime=fetchtime)

@app.route('/tradable/option/<int:id>')
def option(id):
    value = session.query(OptionData).get(id)
    return render_template('option.html', value=value)


def getchain(name='SPY'):
    ''' Get the most recent options chain for the given tradable
    '''
    tradable = session.query(Tradable).filter_by(name=name).first()

    # Get All Option IDs for this Tradable:
    print('Fetching %s Options...' % tradable.name)
    query = session.execute("SELECT id FROM options WHERE tradable_id=%s;" % tradable.id)
    optionids = [str(id) for (id,) in query]

    # Get the Time of The Most Recent Options Data Query For this Tradable:
    print('Determining Most Recent Fetch Time...')
    query = session.execute("SELECT MAX(time) FROM options_data WHERE option_id IN (%s);" % ', '.join(optionids))
    mostrecent = list(query)[0][0]
    print('Most recent Fetch Was: %s' % mostrecent)

    # Get the options data ids for the most recent fetch:
    print('Fetching Most Recent Fetch Options Data IDs...')
    query = session.execute("SELECT id FROM options_data WHERE time='%s';" % str(mostrecent))
    dataids = [int(id) for (id,) in query]

    # Get all the options Values:
    print('Collecting Options Data Records From Most Recent API Fetch...')
    values = session.query(OptionData).filter(OptionData.id.in_(dataids)).all()

    mostrecent -= relativedelta(hours=5)
    fetchtime = mostrecent.strftime('%B %d at %I:%M Central')

    # values = random.sample(values, 1000)
    values.sort(key=lambda item: (item.dte, item.option.type, item.option.strike))
    return values, fetchtime
