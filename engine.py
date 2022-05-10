#############################################
# Website Health - engine.py
# (c)2022, Raskitoma.com
#--------------------------------------------
# Site crawler checker
#-------------------------------------------- 
# TODO  This script should round alongisde the Console
#-------------------------------------------- 
import os
import time
import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
# Include libraries for functionality
from config import logging, \
    db, Events, Wpdata, \
    SLACK_ENABLED, \
    MAIL_ENABLED, \
    send_slack, mail_send, load_sites

# get env variables
WPPLUGINURI = os.environ.get('WPPLUGINURI', 'https://api.wordpress.org/plugins/info/1.2/?action=plugin_information&request[slug]=')

if __name__ == '__main__':
    # Load Sites from db
    sites = json.loads(load_sites())['data']
    # Loop through sites
    for site in sites:
        logging.info(site)
        site_id = site['id']
        site_host = site['host']
        site_path = site['path']
        site_user = site['user']
        site_wp_api = site['wp_api']
        site_path = site_host + site_path
        response = requests.get(site_path, auth=HTTPBasicAuth(site_user, site_wp_api))
        if response.status_code == 200:
            # Site is up
            logging.info('Site is up')
            # Get plugins data
            plugins = json.loads(response.text)
            # Loop through plugins
            outdated_plugins = 0
            outdated_msg = site_host + '\n'
            for plugin in plugins:
                plugin_name = (plugin['plugin']).split('/')[0]
                plugin_version = plugin['version']
                # get source plugin data
                plugin_wp_uri = WPPLUGINURI + plugin_name
                wp_response = requests.get(plugin_wp_uri)
                if wp_response.status_code == 200:
                    wp_plugin = json.loads(wp_response.text)
                    wp_plugin_version = wp_plugin['version']
                    if wp_plugin_version != plugin_version:
                        # Plugin is outdated
                        logging.info('Plugin  is outdated: ' + plugin_name + ' - ' + plugin_version + ' < ' + wp_plugin_version)
                        outdated_plugins += 1
                        outdated_msg += '*' + plugin_name + '* - ' + plugin_version + ' < ' + wp_plugin_version + '\n'
                        # Save event
                        # get timestamp as date string
                        dt_object = datetime.now()
                        event = Events(
                            host=site_host,
                            date=dt_object,
                            object_type='plugin',
                            object_name=plugin_name,
                            object_version=plugin_version,
                            source_version=wp_plugin_version,
                            status='outdated'
                        )
                        db.session.add(event)
                        db.session.commit()
                time.sleep(1)
            if outdated_plugins > 0:
                # Send Slack message
                if SLACK_ENABLED == 'ON':
                    send_slack(outdated_msg)
                # Send email
                if MAIL_ENABLED == 'ON':
                    mail_send(outdated_msg)
        time.sleep(1)
            
#############################################
# EoF