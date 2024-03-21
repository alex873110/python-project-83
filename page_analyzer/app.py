from flask import Flask, render_template, request, flash, redirect
from flask import get_flashed_messages, url_for, abort
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from urllib.parse import urlparse
from page_analyzer.url_functions import normalize_url, validate
import validators
import requests
import os
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def basic():
    title_text = 'Анализатор страниц'
    return render_template('basic.html', title_text=title_text)


@app.get('/urls')
def get_page_urls():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(
          cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cur:
            cur.execute('''SELECT id, name FROM urls ORDER BY id DESC''')
            urls = cur.fetchall()
#        conn.close()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def url_add():
    url_name = request.form.get('url')
    errors = validate(url_name)
    if errors:
        for error in errors:
            flash(error, 'error')
        return render_template(
            'index.html',
            messages=get_flashed_messages(with_categories=True)
        ), 422
    url_normalized = normalize_url(url_name)
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(
          cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cur:
            cur.execute('''SELECT
                        id, name, created_at
                        FROM urls
                        WHERE name = %s''', (url_normalized,))
            url_info = cur.fetchone()
            if url_info:
                conn.close
                flash('Страница уже существует', 'info')
                return render_template(
                 'index.html',
                 messages=get_flashed_messages(with_categories=True)
                )
            cur.execute('''INSERT INTO urls (name, created_at)
                        VALUES (%s, %s) RETURNING id''',
                        (url_normalized, datetime.now())
                        )
            conn.commit()
            id = cur.fetchone()[0]
#        conn.close()
#    flash('Страница успешно добавлена', 'success')
        return redirect(url_for('url_info', id=id))


@app.get('/urls/<id>')
def url_info(id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(
         cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cur:
            cur.execute('''SELECT
                    id, name, created_at
                    FROM urls
                    WHERE id = %s''', (id,))
            url_info = cur.fetchone()
        if not url_info:
            abort(404)
    return render_template(
       'url_info.html',
       url=url_info
    )
