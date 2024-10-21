from flask import Flask, render_template, request, redirect, url_for, make_response
from config import Config
import json
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

config = Config()

def log_to_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        page_name = request.path

        try:
            with open('connections.json', 'r') as log_file:
                logs = json.load(log_file)
        except FileNotFoundError:
            logs = {}

        if page_name in logs:
            logs[page_name] += 1
        else:
            logs[page_name] = 1

        with open('connections.json', 'w') as log_file:
            json.dump(logs, log_file, indent=4)

        return f(*args, **kwargs)

    return decorated_function


with open('links.json', 'r') as file:
    links = json.load(file)


@app.route('/')
@log_to_json
def home():
    return render_template('index.html')


@app.route('/project/albumcoverdownloader')
@log_to_json
def albumCoverDownloader():
    return render_template('AlbumCoverDownloader/index.html')


@app.route('/link/<name>', methods=['GET'])
@log_to_json
def link(name):
    if name.lower() in links:
        url = links[name]
        print(url)
        return redirect(url)
    else:
        return redirect(url_for('home'))
    

@app.route('/sitemap.xml', methods=['GET'])
@log_to_json
def sitemap():
    pages = []
    ten_days_ago = (datetime.now() - timedelta(days=5)).date().isoformat()
    static_urls = [
        'home', 'robots_txt', 'sitemap'
    ]

    for url in static_urls:
        pages.append({
            'loc': url_for(url, _external=True),
            'lastmod': ten_days_ago,
            'changefreq': 'monthly',
            'priority': '1'
        })

    for name in links:
        pages.append({
            'loc': url_for('link', name=name, _external=True),
            'lastmod': ten_days_ago,
            'changefreq': 'monthly',
            'priority': '0.3'
        })

    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


@app.route('/robots.txt')
@log_to_json
def robots_txt():
    response = make_response(
        "User-agent: *\nSitemap: " + url_for('sitemap', _external=True)
    )
    response.headers["Content-Type"] = "text/plain"
    return response



if __name__ == '__main__':
    app.run(debug=config.DEBUG)
