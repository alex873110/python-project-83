from flask import Flask, render_template
# from flask import request, flash, redirect
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def basic():
    title_text = 'Анализатор страниц'
    return render_template('basic.html', title_text=title_text)
