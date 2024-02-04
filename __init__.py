from flask import Flask
#from flask import Flask, flash, redirect, render_template, request, session
import sqlite3
#conn = sqlite3.connect('accounts.db')
#c = conn.cursor()
#user_id_li = c.execute("SELECT * FROM users")
#user_id_l = len(user_id_li)
#print(user_id_l)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hdihhuei'

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app
