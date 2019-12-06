from flask import Flask, render_template
from td.db.models import Tradable, Option, OptionData, OptionsFetch, session
from utils import AppUtils

app = Flask(__name__, template_folder="static/templates")

@app.route('/')
def index():
    ''' Home Page Endpoint
    '''
    # Get the amount of memory used for display:
    gigabytes = AppUtils.memoryused()

    tradables = session.query(Tradable).filter_by(enabled=True).all()
    spy = session.query(Tradable).filter_by(name='SPY').all()
    tradables += spy
    tradables.sort(key=lambda x: x.name)

    ztradables = [(t, None) for t in tradables]

    return render_template('index.html', tradables=ztradables, gigabytes=gigabytes)

@app.route('/tradable/<int:id>')
def tradable(id):
    '''
    '''
    tradable = session.query(Tradable).get(id)
    fetches = sorted(tradable.fetches, key=lambda x: x.time, reverse=True)
    return render_template('history.html', fetches=fetches,  tradable=tradable)


@app.route('/tradable/<int:id>/snapshot/<int:fetchid>')
def tradable_fetch(id, fetchid):
    '''
    '''
    fetch = session.query(OptionsFetch).get(fetchid)
    tradable = fetch.tradable
    assert tradable.id == id
    values = sorted(fetch.values, key=lambda item: (
        item.dte,
        item.option.type,
        item.option.strike
    ))
    fetches = sorted(tradable.fetches, key=lambda x: x.time, reverse=True)
    return render_template(
        'tradable.html',
        tradable=tradable,
        data=values,
        fetchtime=fetch.cststring,
        fetchid=fetchid,
        fetches=fetches,
    )

@app.route('/tradable/option/<int:id>')
def option(id):
    value = session.query(OptionData).get(id)
    return render_template('option.html', value=value)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
