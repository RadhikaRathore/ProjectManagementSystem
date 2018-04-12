#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, jsonify, \
    url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Country, Project, User

# New imports for storing state in login_session

from flask import session as login_session
import random
import string

# imports for getting one time code from client and send responseback to client

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# getting client id from downloaded json file.

CLIENT_ID = \
    json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Project Management System'

# Connect to Database and create database session

engine = create_engine('sqlite:///projectmanagement.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase
                                  + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# will handle post request came to /gconnect.

@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code

    code = request.data

    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'
                                     ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

 # see if user exists, if it doesn't make a new one

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += \
        ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash('you are now logged in as %s' % login_session['username'])
    print 'done!'
    return output


# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email'
                                                             ]).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


# to revoke current users token and their login session

@app.route('/gdisconnect')
def gdisconnect():
    """
    Gathers data from Google Sign In API and places it inside a session variable.
    """
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = \
            make_response(json.dumps('Current user not connected.'),
                          401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'
                                            ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view perticular country's and project's Information

@app.route('/country/<int:country_id>/project/JSON')
def countryProjectJSON(country_id):
    country = session.query(Country).filter_by(id=country_id).one()
    projectprojectitems = \
        session.query(Project).filter_by(country_id=country_id).all()
    return jsonify(Projectprojectitems=[i.serialize for i in
                                        projectprojectitems])


@app.route('/country/<int:country_id>/project/<int:project_id>/JSON')
def projectItemJSON(country_id, project_id):
    Project_Item = session.query(Project).filter_by(id=project_id).one()
    return jsonify(Project_Item=Project_Item.serialize)


@app.route('/country/JSON')
def countryJSON():
    countries = session.query(Country).all()
    return jsonify(countries=[r.serialize for r in countries])


# Show all Countries

@app.route('/')
@app.route('/country/')
def showCountries():
    countries = session.query(Country).order_by(asc(Country.name))
    if 'username' not in login_session:
        return render_template('publiccountries.html',
                               countries=countries)
    else:
        return render_template('countries.html', countries=countries)


# add a new Country

@app.route('/country/new/', methods=['GET', 'POST'])
def newCountry():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCountry = Country(name=request.form['name'],
                             user_id=login_session['user_id'])
        session.add(newCountry)
        flash('New Country %s Successfully Created' % newCountry.name)
        session.commit()
        return redirect(url_for('showCountries'))
    else:
        return render_template('newCountry.html')


# Edit a country

@app.route('/country/<int:country_id>/edit/', methods=['GET', 'POST'])
def editCountry(country_id):
    editedCountry = \
        session.query(Country).filter_by(id=country_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCountry.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this country. Please create your own country in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCountry.name = request.form['name']
            flash('Country Successfully Edited %s' % editedCountry.name)
            return redirect(url_for('showCountries'))
    else:
        return render_template('editCountry.html',
                               country=editedCountry)


# Delete a country

@app.route('/country/<int:country_id>/delete/', methods=['GET', 'POST'])
def deleteCountry(country_id):
    countryToDelete = \
        session.query(Country).filter_by(id=country_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if countryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this country. Please create your own country in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(countryToDelete)
        flash('%s Successfully Deleted' % countryToDelete.name)
        session.commit()
        return redirect(url_for('showCountries', country_id=country_id))
    else:
        return render_template('deleteCountry.html',
                               country=countryToDelete)


# Show a Country's Project

@app.route('/country/<int:country_id>/')
@app.route('/country/<int:country_id>/project/')
def showProject(country_id):
    country = session.query(Country).filter_by(id=country_id).one()
    creator = getUserInfo(country.user_id)
    projectitems = \
        session.query(Project).filter_by(country_id=country_id).all()
    if 'username' not in login_session or creator.id \
            != login_session['user_id']:
        return render_template('publicProject.html',
                               projectitems=projectitems,
                               country=country, creator=creator)
    else:
        return render_template('project.html',
                               projectitems=projectitems,
                               country=country, creator=creator)


# Create a new project

@app.route('/country/<int:country_id>/project/new/', methods=['GET',
                                                              'POST'])
def newProjectItem(country_id):
    if 'username' not in login_session:
        return redirect('/login')
    country = session.query(Country).filter_by(id=country_id).one()
    if login_session['user_id'] != country.user_id:
        return "<script>function myFunction() {\
        alert('You are not authorized to add  projectitems to this country. Please create your own country in order to add projectitems.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newItem = Project(
            name=request.form['name'],
            description=request.form['description'],
            number_of_members=request.form['number_of_members'],
            category=request.form['category'],
            country_id=country_id,
            user_id=country.user_id,
        )
        session.add(newItem)
        session.commit()
        flash('New Project %s Item Successfully Created' % newItem.name)
        return redirect(url_for('showProject', country_id=country_id))
    else:
        return render_template('newProjectItem.html',
                               country_id=country_id)


# Edit a project item

@app.route('/country/<int:country_id>/project/<int:project_id>/edit',
           methods=['GET', 'POST'])
def editProjectItem(country_id, project_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Project).filter_by(id=project_id).one()
    country = session.query(Country).filter_by(id=country_id).one()
    if login_session['user_id'] != country.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit projectitems to this country. Please create your own country in order to edit projectitems.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['number_of_members']:
            editedItem.number_of_members = \
                request.form['number_of_members']
        if request.form['category']:
            editedItem.category = request.form['category']
        session.add(editedItem)
        session.commit()
        flash('Project Item Successfully Edited')
        return redirect(url_for('showProject', country_id=country_id))
    else:
        return render_template('editProjectItem.html',
                               country_id=country_id,
                               project_id=project_id, item=editedItem)


# Delete a project item

@app.route('/country/<int:country_id>/project/<int:project_id>/delete',
           methods=['GET', 'POST'])
def deleteProjectItem(country_id, project_id):
    if 'username' not in login_session:
        return redirect('/login')
    country = session.query(Country).filter_by(id=country_id).one()
    itemToDelete = session.query(Project).filter_by(id=project_id).one()
    if login_session['user_id'] != country.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete projectitems to this country. Please create your own country in order to delete projectitems.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Project Item Successfully Deleted')
        return redirect(url_for('showProject', country_id=country_id))
    else:
        return render_template('deleteProjectItem.html',
                               item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
