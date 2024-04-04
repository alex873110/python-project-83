from flask import Flask, render_template, request, flash, redirect
from flask import get_flashed_messages, url_for, abort
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from page_analyzer.url_functions import normalize_url, validate
from page_analyzer.html_parser import get_seo
import requests
from requests import RequestException
import os
from datetime import datetime
from page_analyzer.db import get_urls, check_db_for_url, insert_url

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def get_page_urls():
    urls = get_urls()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def url_add():
    url_name = request.form.get('url')
    errors = validate(url_name)
    if errors:
        for error in errors:
            flash(error, 'alert-danger')
        return render_template(
            'index.html',
            messages=get_flashed_messages(with_categories=True)
        ), 422
    url_normalized = normalize_url(url_name)
    url_info = check_db_for_url(url_normalized)
    if url_info:
        flash('Страница уже существует', 'alert-info')
        return redirect(url_for('url_info', id=url_info.id))
    id = insert_url(url_normalized)
    flash('Страница успешно добавлена', 'alert-success')
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
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cur:
            cur.execute('''SELECT
                    id, status_code, h1, title, description,
                    created_at FROM url_checks
                    WHERE url_id = %s ORDER BY id DESC''', (id,))
            url_checks = cur.fetchall()
    return render_template(
        'url_info.html',
        url=url_info, url_checks=url_checks,
        messages=get_flashed_messages(with_categories=True),
    )


@app.post('/urls/<id>/checks')
def url_check(id):
    id = int(id)
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cur:
            cur.execute('''SELECT
                    name FROM urls
                    WHERE id = %s''', (id,))
            url_info = cur.fetchone()
            if not url_info:
                abort(404)
            url = url_info.name
        try:
            check = requests.get(url, timeout=(3.05, 10))
            check.raise_for_status()
            status = check.status_code
            title, h1, description = get_seo(check.text)
            with conn.cursor(
                cursor_factory=psycopg2.extras.NamedTupleCursor
            ) as cur:
                cur.execute('''INSERT INTO url_checks (url_id, status_code,
                            h1, title, description, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)''',
                            (id, status, h1, title, description,
                             datetime.now().date())
                            )
            flash('Страница успешно проверена', 'alert-success')
            conn.commit()
        except RequestException:
            flash('Произошла ошибка при проверке', 'alert-danger')
    return redirect(url_for('url_info', id=id))
