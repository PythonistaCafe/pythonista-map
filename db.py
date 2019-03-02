import sqlite3
from flask import current_app, g
from flask.cli import with_appcontext
import click
from datetime import datetime
from os import path


def get_db():
    try:
        if 'db' not in g:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
        g.db.row_factory = sqlite3.Row
        return g.db
    except RuntimeError:
        db = sqlite3.connect(
            './instance/map.sqlite',
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
        return db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    try:
        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
    except RuntimeError:
        with open(path.join(path.dirname(path.realpath(__file__)), 'schema.sql')) as f:
            db.executescript(f.read())


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('DB initialized')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def select_all_data():
    # prints and returns all data from data table
    db = get_db()
    all_data = db.execute(
        'SELECT id, location, latitude, longitude, created FROM data'
    ).fetchall()
    print('selected data: ')
    for each in all_data:
        print('   ', each['id'], each['location'], each['latitude'],
              each['longitude'], each['created'])
    return all_data


def insert_into_data(location, latitude, longitude):
    db = get_db()
    db.execute(
        'INSERT INTO data (location, latitude, longitude, created) VALUES (?, ?, ?, ?)',
        (location, latitude, longitude, datetime.utcnow())
    )
    db.commit()
    return True


def select_map_data():
    # used for MarkerCluster points generation
    db = get_db()
    all_data = db.execute(
        'SELECT latitude, longitude FROM data'
    ).fetchall()
    map_data = []
    for each in all_data:
        map_data.append([each['latitude'], each['longitude']])
    return map_data
