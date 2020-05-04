# Assignemnt 1
A public health record demonstration system with the use of a CP-ABE scheme.

## Installation
The steps below have been verified under OSX 10.9 and Ubuntu 13.10 x64. Python 2.7 and NodeJS with NPM are required.

* Clone this repository and navigate to this directory
* `pip install -r requirements.txt`
* Install Charm Crypto (see www.charm-crypto.com/Documentation.html)
* Install Django JSON RPC (see https://github.com/samuraisam/django-json-rpc)
* Navigate to `client` directory
  * `python manage.py syncdb`
  * `npm -g install bower`
  * `python manage.py bower_install`
  * Make sure the data directory exists
* Navigate to the `server` directory
  * `python manage.py syncdb`
  
## Running
Two servers must be started.

* Navigate to `client` directory
  * `python manage.py runserver 8001`
  * Make sure the data directory exists
* Navigate to the `server` directory
  * `python manage.py runserver 8000`
  
Then, navigate to `http://127.0.0.1:8001` to use the web GUI. The URL of the server is `http://127.0.0.1:8000`. This is used during creating and connecting to a PHR via the web GUI or command line interface.

## Command line interface
This demonstrator can be used without running the client web server. In this case, navigate to the `client` directory and issue one of the following commands.

* `python manage.py phr_connect <data_file> <host>`
* `python manage.py phr_create <data_file> <host> <record_name>`
* `python manage.py phr_decrypt <data_file> <record_item_id>`
* `python manage.py phr_encrypt <data_file> <category> <parties> <message>`
* `python manage.py phr_grant <data_file> <category> <parties>`
* `python manage.py phr_list <data_file> <category> <parties>`
* `python manage.py phr_retrieve <data_file> <category>`
* `python manage.py phr_status <data_file>`

Additional help can be viewed via `manage.py help <command_name>`, e.g. `manage.py help phr_connect`.

## Files of importance
The following files are of importance to the assignment.

* `client/protocol.py` &mdash; The layer between the user and the CP-ABE scheme. Handles setup, keygen, encryption and decryption
* `client/actions.py` &mdash; Responsible for most operations between the server and the protocol.
* `client/data_file.py` &mdash; Wrapper for the local key store.
* `client/utils.py` &mdash; Several utilities, including padding and more.
* `client/tests.py` &mdash; Tests for a great share of the above mentioned files
* `server/api.py` &mdash; Interface between a party and the server.
* `server/settings.py` &mdash; Server configuration file. Bottom part defines the categories, parties and mappings.

Most of the files are documented. The tests covers most (at least the required) functionality. Test can be run via `python manage.py test` in the `client` or `server` directory.

