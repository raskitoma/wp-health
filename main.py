#############################################
# Website Health - main.py
# (c)2022, Raskitoma.com
#--------------------------------------------
# Site crawler - Main Script / Dashboard
#-------------------------------------------- 
# TODO  This script should control the engine
#-------------------------------------------- 

# Include libraries for functionality
from config import app, logging, \
    db, Sites, Events, Wpdata, \
    APP_PORT, \
    CHECK_MODE, \
    check_process, load_sites

import sys
from flask import make_response, render_template, request, \
    Response, send_from_directory

if check_process():
    CHECK_MODE = 'ON'
    sys.exit('Process already running')
else:
    CHECK_MODE = 'OFF'

@app.route('/')
def index():
    return render_template('status.html', check_status_mode=CHECK_MODE)

@app.route('/assets/js/<path:path>')
def send_js(path):
    return send_from_directory('assets/js', path)

@app.route('/assets/bootstrap/<path:path>')
def send_bs(path):
    return send_from_directory('assets/bootstrap', path)

@app.route('/assets/css/<path:path>')
def send_css(path):
    return send_from_directory('assets/css', path)

@app.route('/assets/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('assets/fonts', path)

@app.route('/config')
def config():
    return render_template('config.html')

@app.route('/wcenable', methods=['GET'])
def wcenable():
    global CHECK_MODE
    CHECK_MODE = 'ON'
    os.environ['CHECK_MODE'] = 'ON'
    return Response(status=200)

@app.route('/wcdisable', methods=['GET'])
def wcdisable():
    global CHECK_MODE
    CHECK_MODE = 'OFF'
    os.environ['CHECK_MODE'] = 'OFF'
    return Response(status=200)

# TODO This is the beggining of the data handling check any issues
# TODO Add data handling for queries about sites health and other data

@app.route('/sites', methods=['POST', 'GET'])
def sites():
    if request.method == 'POST':
        db.session.add(Sites(
            host = request.form['site_host'],
            path = request.form['site_path'],
            user = request.form['site_user'],
            wp_api = request.form['site_wp_api']
        ))
        logging.info('Added site: ' + request.form['site_host'])
        db.session.commit()
    response = make_response(load_sites(), 200)
    response.mimetype = 'application/json'
    # response.mimetype = 'text/plain'
    return response
    
@app.route('/sites/edit/<int:id>', methods=['GET', 'POST'])
def sites_edit(id):
    site = Sites.query.get(id)
    if request.method == 'POST':
        site.host = request.form['site_host']
        site.path = request.form['site_path']
        site.user = request.form['site_user']
        site.wp_api = request.form['site_wp_api']
        db.session.commit()
    return load_sites()

@app.route('/sites/delete/<int:id>', methods=['DELETE'])
def sites_delete(id):
    site = Sites.query.get(id)
    db.session.delete(site)
    db.session.commit()
    return load_sites()

if __name__ == '__main__':
    app.run(debug=True, port=APP_PORT)

#############################################
# EoF    