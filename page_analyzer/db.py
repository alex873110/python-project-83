import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


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
    with conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    ) as cur:
        cur.execute('''SELECT DISTINCT ON (url_id)
            url_id, status_code, created_at
            FROM url_checks
            ORDER BY url_id, created_at DESC;''')
        last_checks = cur.fetchall()
    for url in urls:
        for last_check in last_checks:
            if url['id'] == last_check['url_id']:
                url['check_date'] = last_check['created_at'].date()
                url['status_code'] = last_check['status_code']
    return urls


def check_db_for_url(url_name):
    conn = get_connection()
    with conn.cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor
    ) as cur:
        cur.execute('''SELECT
                        id FROM urls
                        WHERE name = %s''', (url_name,))
        url_info = cur.fetchone()
    return url_info


def insert_url(url_name):
    conn = get_connection()
    with conn.cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor
    ) as cur:
        cur.execute('''INSERT INTO urls (name, created_at)
                    VALUES (%s, %s) RETURNING id''',
                    (url_name, datetime.now())
                    )
        conn.commit()
        id = cur.fetchone()[0]
    return id


def get_url_by_id(id):
    conn = get_connection()
    with conn.cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor
    ) as cur:
        cur.execute('''SELECT
                id, name, created_at
                FROM urls
                WHERE id = %s''', (id,))
        url_info = cur.fetchone()
    return url_info


def get_url_checks(id):
    conn = get_connection()
    with conn.cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor
    ) as cur:
        cur.execute('''SELECT
                    id, status_code, h1, title, description,
                    created_at FROM url_checks
                    WHERE url_id = %s ORDER BY id DESC''', (id,))
        url_checks = cur.fetchall()
    return url_checks


def insert_check(id, status, h1, title, description):
    conn = get_connection()
    with conn.cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor
    ) as cur:
        cur.execute('''INSERT INTO url_checks (url_id,status_code,
                    h1, title, description, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)''',
                    (id, status, h1, title, description,
                     datetime.now().date()))
        conn.commit()
