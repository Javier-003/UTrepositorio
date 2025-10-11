from flask import Blueprint, render_template, redirect, url_for

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')
