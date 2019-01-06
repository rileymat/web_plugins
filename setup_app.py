#!/usr/bin/python

import argparse
from distutils.util import strtobool
import os
import readline

####### Helper functions ##############
def write_file(filename, content):
	with open(filename, 'w') as text_file:
		text_file.write(content)

def write_executable(filename, content):
	write_file(filename, content)
	os.system('chmod +x ' + filename)

def input_or_default(prompt, default=''):
	if (default != ''):
		prompt = prompt + ' (default=' + default +')'
	prompt = prompt + ': '
	return raw_input(prompt).strip() or default

def get_arguments():
	parser = argparse.ArgumentParser(description='Setup web plugins app.')
	
	parser.add_argument('--generate-basic-site', dest='generate_basic_site', action='store_true')
	parser.add_argument('--no-generate-basic-site', dest='generate_basic_site', action='store_false')

	parser.add_argument('--create-git-repo', dest='create_git_repo', action='store_true')
	parser.add_argument('--no-create-git-repo', dest='create_git_repo', action='store_false')
	parser.set_defaults(generate_basic_site=True, create_git_repo=True)

	parser.add_argument('--app-name', dest='app_name', default='app')
	args = parser.parse_args()
	return args
########################################

args = get_arguments()
app_name = args.app_name
generate_basic_site = args.generate_basic_site
create_git_repo = args.create_git_repo

working_directory = os.getcwd()
static_directory  = 'static'

######### Get info from user #############
app_name = input_or_default('Enter app name', app_name)
host_name = input_or_default('Enter Host Name', app_name + '.oscmp.com')
run_server_port = input_or_default('Enter run server port', '8001')
create_git_repo = strtobool(input_or_default('Create git repo', 'y' if create_git_repo else 'n'))
if create_git_repo:
	create_github_repo = strtobool(input_or_default('Create github repo', 'n'))
	if create_github_repo:
		github_username = ''
		while (github_username == ''): github_username = input_or_default('Github username', '')
		github_repo_name = ''
		while (github_repo_name == ''): github_repo_name = input_or_default('Github repo name', app_name)

add_to_nginx = strtobool(input_or_default('Add to Nginx', 'y'))
if add_to_nginx:
	nginx_config_location = input_or_default('Nginx Config Location', '/etc/nginx/sites-enabled')
	restart_nginx_command = input_or_default('Nginx Restart Command', 'sudo service nginx restart')

add_to_host_file = strtobool(input_or_default('Add to host file', 'y'))
add_to_upstart = strtobool(input_or_default('Add to upstart', 'y'))
add_to_systemd = strtobool(input_or_default('Add to systemd', 'y'))
##########################################



####### File templates ##################
run_server = """source virtual_env/bin/activate
uwsgi --http 127.0.0.1:{run_server_port} --wsgi-file {app_name}.py  --honour-stdin --async 10 --gevent 1000
""".format(app_name=app_name, run_server_port=run_server_port)

run_server_nginx = """#!/bin/bash
cd {working_directory}
source virtual_env/bin/activate
uwsgi --socket virtual_env/{app_name}.sock --wsgi-file {app_name}.py --chmod-socket=666 --async 10 --gevent 1000
""".format(app_name=app_name, working_directory=working_directory)

nginx_config ="""
upstream web_plugin_app_{app_name}{{
    server unix://{working_directory}/virtual_env/{app_name}.sock; # for a file socket
}}
server {{
    # the port your site will be served on
    listen      80;
    # the domain name it will serve for
    server_name {host_name}; # substitute your machine's IP address or FQDN
    root {working_directory};
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;   # adjust to taste
    location / {{
         try_files /{static_directory}$uri @web_plugins;
         #error_page 404 = @web_plugins;
     }}
    location @web_plugins {{

        uwsgi_pass   web_plugin_app_{app_name};
        uwsgi_param  QUERY_STRING       $query_string;
        uwsgi_param  REQUEST_METHOD     $request_method;
        uwsgi_param  CONTENT_TYPE       $content_type;
        uwsgi_param  CONTENT_LENGTH     $content_length;

    	uwsgi_param  REQUEST_URI        $request_uri;
        uwsgi_param  PATH_INFO          $document_uri;
        uwsgi_param  DOCUMENT_ROOT      $document_root;
        uwsgi_param  SERVER_PROTOCOL    $server_protocol;
        uwsgi_param  HTTPS              $https if_not_empty;
 
    	uwsgi_param  REMOTE_ADDR        $remote_addr;
    	uwsgi_param  REMOTE_PORT        $remote_port;
    	uwsgi_param  SERVER_PORT        $server_port;
    	uwsgi_param  SERVER_NAME        $server_name;

    }}
}}
""".format(app_name=app_name, working_directory=working_directory, static_directory=static_directory, host_name=host_name)

basic_site = """
import web_plugins.app
from web_plugins.app import application
from web_plugins.response import HtmlResponse
import web_plugins.router as r

def {app_name}(request):
	response = HtmlResponse()
	response.response_text = "{app_name} feels great."
	return response

static_router = r.FileRoute('/','./{static_directory}')
router = r.FirstMatchRouter()
router.routes.extend([static_router, r.Route({app_name})])
application.handler = router

""".format(app_name=app_name, static_directory=static_directory)

git_ignore = """
virtual_env/
*.pyc
run_server
run_server_nginx
*.conf
cleanup.sh
"""

upstart_config = """description "Handles Web Plugin {app_name}"
start on runlevel [2345]
stop on runlevel [06]

script
	exec bash -c {working_directory}/run_server_nginx
end script
""".format(app_name=app_name, working_directory=working_directory)

systemd_config = """
[Unit]
Description=uWSGI instance to serve {app_name}

[Service]
ExecStart={working_directory}/run_server_nginx
Restart=always

[Install]
WantedBy=multi-user.target
""".format(app_name=app_name, working_directory=working_directory)

cleanup_script_template = """
rm {app_name}_nginx.conf
rm run_server
rm run_server_nginx
rm -rf virtual_env
sudo rm {nginx_config_location}/{app_name}_nginx.conf
{host_file_line}
{upstart_line}
rm cleanup.sh 
"""
###################################################


############  Write Files  #########################

if add_to_nginx:
	write_executable('run_server_nginx', run_server_nginx)
	write_file('{}_nginx.conf'.format(app_name), nginx_config)

write_executable('run_server', run_server)

if generate_basic_site:
	write_executable('{}.py'.format(app_name), basic_site.format(app_name=app_name))
	os.system('mkdir {static_directory}'.format(static_directory=static_directory))

if add_to_nginx:
	os.system('sudo ln -s {0}/{1}_nginx.conf {2}/{1}_nginx.conf'.format(working_directory, app_name, nginx_config_location))
	os.system(restart_nginx_command)

if add_to_host_file:
	host_line = '127.0.0.1 ' + host_name
	os.system('echo "' + host_line + '" | sudo tee -a /etc/hosts');


if add_to_systemd:
	systemd_config_name = '{app_name}_uwsgi_nginx'.format(app_name=app_name)
	systemd_config_file_name = systemd_config_name + '.system'
	write_file(systemd_config_file_name, systemd_config)
	os.system('sudo cp {working_directory}/{systemd_config_file_name} /etc/systemd/system/{systemd_config_file_name}'.format(systemd_config_file_name = systemd_config_file_name, working_directory=working_directory))
	os.system('sudo systemctl daemon-reload')
	os.system('sudo systemctl start {systemd_config_name}'.format(systemd_config_name=systemd_config_name))
	
if add_to_upstart:
	upstart_config_name = '{app_name}_uwsgi_nginx'.format(app_name=app_name)
	upstart_config_file_name = upstart_config_name + '.conf'
	write_file(upstart_config_file_name, upstart_config)
	os.system('sudo cp {working_directory}/{upstart_config_file_name} /etc/init/{upstart_config_file_name}'.format(upstart_config_file_name = upstart_config_file_name, working_directory=working_directory))
	os.system('sudo initctl reload-configuration')
	os.system('sudo start {upstart_config_name}'.format(upstart_config_name=upstart_config_name))

os.system("sed -i -e 's/^setup_app.py$/setup_app.py --no-generate-basic-site --no-create-git-repo --app-name={app_name}/g' bootstrap.sh".format(app_name=app_name))


upstart_line = 'rm {upstart_config_file_name}\nsudo rm /etc/init/{upstart_config_file_name}'.format(upstart_config_file_name=upstart_config_file_name) if add_to_upstart else ''
systemd_line = 'rm {systemd_config_file_name}\nsudo rm /etc/systemd/system/{systemd_config_file_name}'.format(systemd_config_file_name=systemd_config_file_name) if add_to_systemd else ''
host_file_line = "sudo sed -i '/{host_line}/d' /etc/hosts".format(host_line=host_line) if add_to_host_file else ''

if create_git_repo:
	write_file('.gitignore', git_ignore)
	os.system('git init')
	os.system('git add .')
	os.system("git commit -am 'Initial auto commit.'")
	if create_github_repo:
		os.system("""curl -u '{github_username}' https://api.github.com/user/repos -d '{{"name":"{repo_name}"}}'""".format(github_username=github_username,repo_name=github_repo_name))
		os.system('git remote add origin git@github.com:{github_username}/{repo_name}.git'.format(github_username=github_username, repo_name=github_repo_name))
		os.system('git push origin master')

write_executable('cleanup.sh', 
				 cleanup_script_template.format(app_name=app_name, 
												host_name=host_name, 
												nginx_config_location=nginx_config_location, 
												upstart_config_file_name=upstart_config_file_name,
												upstart_line=upstart_line,
												systemd_line=systemd_line,
												host_file_line=host_file_line
											)
				 )
