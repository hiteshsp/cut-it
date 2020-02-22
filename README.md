# Welcome to the URL Shortener

This application is built to shorten the URL's like bitly, goo.gl. It's simple, intuitive and efficient. It's built using Flask.

Hope you like it :)

## Features

* Generates the short url randomly without any conflicts
* Uses NoSQL DynamoDB for easier storage and retrieval
* Doesn't generate a short url if it exists already
* Visualizes the URL hits in the form of pie chart
* Contains a statisics page for all short urls generated and individual URL's too

## Built on
* Python3
* [Flask](https://flask.palletsprojects.com)
* Jinja2
* [Bootstrap 4](getbootstrap.com/)
* [Google Charts](https://developers.google.com/chart)
* [MomentJS](https://momentjs.com/)

## Requirements

* AWS DynamoDB
* Python3 with pip installed.
* Any OS


## Installation

### Fetching the Dependencies

Install the Virtualenv module
``` 
   $ pip install virtualenv
```
Change the Directory to App
```
   $ cd flask-app
```
Initialize the virtual environment in project directory and install the dependencies
```
   $ python3 -m venv venv
   $ source venv/bin/activate
   $ pip install -r requirements.txt    
```

### Configuring the Environment Variables
```
   $ export TABLE_NAME = <enter the dynamodb table name>
   $ export SECRET_KEY = <enter your secret key>
   $ export AWS_DEFAULT_REGION = <enter your AWS region>
   $ export IP = <enter the public ip address of the server>
```

### Running the Server

#### Development Mode

The following command is to run the development server
```
    $ python run.py
```
#### Production Mode

To run flask in production we need to configure an application server. Here we are using [gunicorn](https://gunicorn.org/).

More details on configuring gunicorn can be found [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)


To start gunicorn, run the following command

```
    $ gunicorn --bind 0.0.0.0:5000 wsgi:app
```

## Authors

* **Hiteshwara Sharma** - (https://github.com/hiteshsp)
