from flask import Flask, render_template, request, flash, redirect
 
app = Flask(__name__)
 
 
@app.route('/')
def basic():
    title_text = 'Анализатор страниц'
    return render_template('basic.html', title_text=title_text)
