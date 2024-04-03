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


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def get_urls():
    conn = get_connection()
    with conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    ) as cur:
        cur.execute('''SELECT id, name FROM urls ORDER BY id DESC''')
        urls = cur.fetchall()
        cur.close()
    for url in urls:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
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
    return urls

