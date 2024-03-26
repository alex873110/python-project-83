from flask import Flask, render_template, request, flash, redirect
from flask import get_flashed_messages, url_for, abort
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from urllib.parse import urlparse
from page_analyzer.url_functions import normalize_url, validate
from page_analyzer.html_parser import get_seo
import validators
import requests
from requests import RequestException
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
          cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute('''SELECT id, name FROM urls ORDER BY id DESC''')
            urls = cur.fetchall()
            cur.close()
        for url in urls:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                query = '''SELECT status_code, created_at
                   FROM url_checks
                   WHERE url_id = (%s)
                   ORDER BY id DESC;
                '''
                cur.execute(query, [url['id']])
                last_check = cur.fetchone()
                if last_check:
                    url['check_date'] = last_check['created_at'].date()
                    url['status_code'] = last_check['status_code']
                else:
                    url['check_date'] = ''
                    url['status_code'] = ''
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
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(
          cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cur:
            cur.execute('''SELECT
                        id FROM urls
                        WHERE name = %s''', (url_normalized,))
            url_info = cur.fetchone()
            if url_info:
                conn.close
                flash('Страница уже существует', 'alert-info')
                return redirect(url_for('url_info', id=url_info.id))
            cur.execute('''INSERT INTO urls (name, created_at)
                        VALUES (%s, %s) RETURNING id''',
                        (url_normalized, datetime.now())
                        )
            conn.commit()
            id = cur.fetchone()[0]
#        conn.close()
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
        with conn.cursor() as cur:
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
            check = requests.get(url)
            status = int(check.status_code)
            url_data = get_seo(check.text)
            title = url_data('title')
            h1 = url_data('h1')
            description = url_data('description')
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
