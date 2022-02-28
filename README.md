# Encryptino API
### Easily encrypt and decrypt your private messages

##Usage
+ In order to create an environment for libraries you need create one:
```console
$ python3 -m venv env
$ source env/bin/activate
```
>Note, that I am using python3 (If you have a single python v3 without python v2, you can just type `python`)
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
