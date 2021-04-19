import os
import logging
from flask import Flask, request, render_template, redirect, flash, session, make_response
from td.db.models import Tradable, Option, OptionData, OptionsFetch, Token, session
from utils import AppUtils
from auth import FlaskAuth


app = Flask(__name__, template_folder="static/templates")

# Set app secret key for message flashing:
app.secret_key = os.urandom(24)

# Initialize Logger:
logging.basicConfig(level=logging.INFO)

@app.route('/login', methods=['GET', 'POST'])
def login():
    ''' Login Endpoint API
    '''
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        auth = FlaskAuth.authenticate(username, password)
        if auth:
            response = make_response()
            for cookie, value in auth.cookies.iteritems():
                response.set_cookie(cookie, value)

            response.headers['location'] = '/'

            flash('Credential Accepted', 'success')
            return response, 302
        else:
            flash('Incorrect Username/Password', 'error')
            return redirect('/login')

@app.route('/logout')
def logout():
    ''' Login Endpoint API
    '''
    # Do deauthentication:
    FlaskAuth.deauthenticate()

    # Make response & drop all cookies:
    response = make_response()
    for cookie, value in request.cookies.iteritems():
        response.set_cookie(cookie, '')
    response.headers['location'] = '/login'

    flash('Successfully Logged Out', 'info')
    return response, 302


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
    return render_template('index.html', tradables=tradables, gigabytes=gigabytes)

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
    ''' Single-Option Detail View
    '''
    value = session.query(OptionData).get(id)
    return render_template('option.html', value=value)

@app.route('/tokens')
def tokens():
    ''' Current API Token Details
    '''
    tokens = session.query(Token).all()
    tokens.sort(key=lambda token: token.date, reverse=True)
    return render_template('tokens.html', tokens=tokens)


# Setup authentication:
app.before_request(FlaskAuth.checkauth)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
