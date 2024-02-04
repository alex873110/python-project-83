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


@app.post('/urls')
def url_add():
    url_name = request.form.get('url')
    errors = validate(url_name)
    if errors:
        for error in errors:
            flash(error, 'error')
        return render_template(
            'basic.html',
        ), 422
    url_parsed = urlparse(url_name)
    url_name = f'{url_parsed.scheme}://{url_parsed.netloc}'
    with connect(DATABASE_URL) as conn:
        url_to_check = db.get_url_by_name(conn, url_name)
        if url_to_check:
            flash('Страница уже существует', 'info')
            return redirect(url_for('url_info', id=url_to_check[0]))
        url_id = db.create_url(conn, url_name)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url_info', id=url_id))



@app.get('/urls/<id>')
def url_info(id):
    with connect(DATABASE_URL) as conn:
        url = db.get_url_by_id(conn, id)
        if not url:
            abort(404)
        url_checks = db.get_checks_by_url_id(conn, id)
    return render_template(
        'urls_id.html',
        url=url,
        checks=url_checks
    )
