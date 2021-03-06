# Encryption API
### Easily encrypt and decrypt your private messages

## Installation
### Running django server

+ In order to create an environment for libraries you need create one in main folder:
```console
$ python3 -m venv env
$ source env/bin/activate
```
>Note, that I am using python3 (If you have a single python v3 without python v2, you can just type `python`)
+ Install required libraries:
```console
$ pip install -r requirements.txt
```
+ After that you can start the migrations:
```console
$ python3 manage.py makemigrations verify
$ python3 manage.py migrate verify
$ python3 manage.py migrate
```

+ From now on, you are ready to go:
```console
$ python3 manage.py runserver
```

<hr>

### Running rabbitmq and celery
>Note, that you need RabbitMQ broker be installed in your OS

+ Firstly, open up new shell and start RabbitMQ server:
```console
$ sudo systemctl start rabbitmq-server 
```
You can check whether it is working or not by:
```console
$ sudo systemctl status rabbitmq-server 
```
+ Open new shell, then go to the main folder directory of project and activate virtual environment, you've already installed:
 ```console
$ source env/bin/activate
```
+ After that you may start hearing with celery by typing:

```console
$ celery -A config  worker -l info
```
Go to the link [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/ "Visit the documentation!") to see the documentation of Encryption API


<hr>

*If you have any questions related to the usage of this API, feel free to contact me:*

*Telegram: [@youngerwolf](https://t.me/youngerwolf "Contact me via telegram!")*

*Gmail: [milsolve@gmail.com](mailto:milsolve@gmail.com "Contact me via gmail!")*

