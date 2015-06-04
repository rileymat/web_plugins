#!/usr/bin/python


from distutils.util import strtobool
import readline
import os


import argparse

parser = argparse.ArgumentParser(description='Setup web plugins app.')
parser.add_argument('--generate-basic-site', dest='generate_basic_site', action='store_true')
parser.add_argument('--no-generate-basic-site', dest='generate_basic_site', action='store_false')
parser.set_defaults(generate_basic_site=True)

parser.add_argument('--app-name', dest='app_name', default='app')

args = parser.parse_args()

app_name = args.app_name
generate_basic_site = args.generate_basic_site



working_directory = os.getcwd()

def input_or_default(prompt, default=''):
	if (default != ''):
		prompt = prompt + ' (default=' + default +')'
	prompt = prompt + ': '
	return raw_input(prompt).strip() or default

app_name = input_or_default('Enter App Name', app_name)
host_name = input_or_default('Enter Host Name', app_name + '.oscmp.com')
nginx_config_location = input_or_default('Nginx Config Location', '/etc/nginx/sites-enabled')
restart_nginx_command = input_or_default('Nginx Restart Command', 'sudo service nginx restart')
add_to_host_file = input_or_default('Add to host file', 'y')
add_to_upstart = input_or_default('Add to upstart', 'y')
run_server_template = """source virtual_env/bin/activate
uwsgi --http 127.0.0.1:8001 --wsgi-file {}.py  --honour-stdin --async 10 
""".format(app_name)

run_server_nginx_template = """cd {working_directory}
source virtual_env/bin/activate
uwsgi --socket virtual_env/{app_name}.sock --wsgi-file {app_name}.py --chmod-socket=666 --async 10
""".format(app_name=app_name, working_directory=working_directory)



nginx_config_template ="""
upstream web_plugin_app_{app_name}{{
    server unix://{working_directory}/virtual_env/{app_name}.sock; # for a file socket
}}
server {{
    # the port your site will be served on
    listen      80;
    # the domain name it will serve for
    server_name {app_name}.oscmp.com; # substitute your machine's IP address or FQDN
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;   # adjust to taste

    #  location /static {{
    #      alias /path/to/your/mysite/static; # your Django project's static files - amend as required
    #  }}

    # Finally, send all non-media requests to the Django server.
    location / {{
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
""".format(app_name=app_name, working_directory=working_directory)

basic_site_template = """
import web_plugins.app
from web_plugins.app import application
from web_plugins.response import HtmlResponse


def {app_name}(request):
	response = HtmlResponse()
	response.response_text = "{app_name} feels great."
	return response

application.handler = {app_name}
""".format(app_name=app_name)

git_ignore_template = """
virtual_env/
*.pyc
run_server
run_server_nginx
*.conf
cleanup.sh
"""


def write_file(filename, content):
	with open(filename, 'w') as text_file:
		text_file.write(content)
def write_executable(filename, content):
	write_file(filename, content)
	os.system('chmod +x ' + filename)


write_executable('run_server_nginx', run_server_nginx_template)
write_executable('run_server', run_server_template)
write_file('{}_nginx.conf'.format(app_name), nginx_config_template)
write_file('.gitignore', git_ignore_template)

if generate_basic_site:
	write_executable('{}.py'.format(app_name), basic_site_template.format(app_name=app_name))


os.system('sudo ln -s {0}/{1}_nginx.conf {2}/{1}_nginx.conf'.format(working_directory, app_name, nginx_config_location))
os.system(restart_nginx_command)

host_line = '127.0.0.1 ' + host_name

if strtobool(add_to_host_file):
	os.system('echo "' + host_line + '" | sudo tee -a /etc/hosts');


upstart_config = """description "Handles Web Plugin {app_name}"
start on runlevel [2345]
stop on runlevel [06]

script
	exec bash -c {working_directory}/run_server_nginx
end script
""".format(app_name=app_name, working_directory=working_directory)

use_upstart = strtobool(add_to_upstart)
if use_upstart:
	upstart_config_name = '{app_name}_uwsgi_nginx'.format(app_name=app_name)
	upstart_config_file_name = upstart_config_name + '.conf'
	write_file(upstart_config_file_name, upstart_config)
	os.system('sudo cp {working_directory}/{upstart_config_file_name} /etc/init/{upstart_config_file_name}'.format(upstart_config_file_name = upstart_config_file_name, working_directory=working_directory))
	os.system('sudo initctl reload-configuration')
	os.system('sudo start {upstart_config_name}'.format(upstart_config_name=upstart_config_name))

os.system("sed -i -e 's/^setup_app.py$/setup_app.py --no-generate-basic-site --app-name={app_name}/g' bootstrap.sh".format(app_name=app_name))

cleanup_script = """
rm {app_name}_nginx.conf
rm {app_name}.py
rm run_server
rm run_server_nginx
rm -rf virtual_env
sudo rm {nginx_config_location}/{app_name}_nginx.conf
sudo sed -i '/{host_line}/d' /etc/hosts
rm {upstart_config_file_name}
{upstart_line}
rm cleanup.sh 
""".format(app_name=app_name, host_name=host_name, nginx_config_location=nginx_config_location, host_line=host_line, 
           upstart_config_file_name=upstart_config_file_name,
		   upstart_line='sudo rm /etc/init/' + upstart_config_file_name if use_upstart else '')

write_executable('cleanup.sh', cleanup_script)
