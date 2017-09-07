import calendar
import dateparser
import json
import logging
import os
import six
try:
    from lz4.block import decompress
except ImportError:
    try:
        from lz4 import decompress
    except ImportError:
        def decompress(data):
            return data

from flask import Flask, request, jsonify, render_template
from flamegraphviewer.backends import get_db

app = Flask(__name__)
app.config['DEBUG'] = True

def _parse_relative_date(datestr):
    return calendar.timegm(dateparser.parse(datestr).utctimetuple())

class Node(object):
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.children = {}

    def serialize(self, threshold=None):
        res = {
            'name': self.name,
            'value': self.value
        }
        if self.children:
            serialized_children = [
                child.serialize(threshold)
                for _, child in sorted(self.children.items())
                if child.value > threshold
            ]
            if serialized_children:
                res['children'] = serialized_children
        return res

    def add(self, frames, value):
        self.value += value
        if not frames:
            return
        head = frames[0]
        child = self.children.get(head)
        if child is None:
            child = Node(name=head)
            self.children[head] = child
        child.add(frames[1:], value)

    def add_raw(self, line):
        frames, value = line.split()
        frames = frames.split(';')
        try:
            value = int(value)
        except ValueError:
            return
        self.add(frames, value)

@app.route('/keys')
def keys():
    key_filter = request.args.get('filter', None)
    if not key_filter:
        key_filter='*'
    with get_db(app.config['DB_URL']) as db:
        keys = [key.decode('utf-8') for key in db.scan_iter(key_filter)]
        return jsonify(keys)

@app.route('/data', methods=['GET', 'POST'])
def data():
    from_ = request.args.get('from')
    if from_ is None:
        from_ = '-inf'
    else:
        from_ = _parse_relative_date(from_)

    until = request.args.get('until')
    if until is None:
        until = '+inf'
    else:
        until = _parse_relative_date(until)
    threshold = float(request.args.get('threshold', 0))
    try:
        request_data = json.load(six.BytesIO(request.data))
    except json.decoder.JSONDecodeError:
        request_data = {}

    root = Node('root')
    with get_db(app.config['DB_URL']) as db:
        for key in request_data.get('keys', []):
            for el in db.zrangebyscore(key, from_, until):
                with six.StringIO(decompress(el).decode()) as data:
                    for line in data:
                        root.add_raw(line)

    return jsonify(root.serialize(threshold * root.value))


@app.route('/')
def render():
    return app.send_static_file('index.html')


def run(port, db_url):
    app.config['DB_URL'] = db_url
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    run(int(os.getenv('PORT', 9999)),  str(os.getenv('DB_URL', '')))
