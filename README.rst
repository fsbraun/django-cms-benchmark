|pythonapp|

####################
django CMS benchmark
####################

A dockerised django CMS project to benchmark performance for large installations.

This project is based on the `django CMS quickstart <https://github.com/django-cms/django-cms-quickstart>`_ and
add a benchmark app.

Benchmarks are run on the existing database by typing::

    docker compose run web python manage.py test


Installation
############

You need to have Docker installed on your system to run this project.

- `Install Docker <https://docs.docker.com/engine/install/>`_ here.
- If you have not used docker in the past, please read this
  `introduction on docker <https://docs.docker.com/get-started/>`_  here.

Try it
######

.. inclusion-marker-do-not-remove

.. code-block:: bash

  git clone git@github.com:django-cms/django-cms-quickstart.git
  cd django-cms-quickstart
  docker compose build web
  docker compose up -d database_default
  docker compose run web python manage.py migrate
  docker compose run web python manage.py createsuperuser
  docker compose up -d

Then open http://django-cms-quickstart.127.0.0.1.nip.io:8000 (or just http://127.0.0.1:8000) in your browser.

You can stop the server with ``docker compose stop`` without destroying the containers and restart it with
``docker compose start``.

With ``docker compose down`` the containers are deleted, but the database content is still preserved in the named
volume ``django-cms-quickstart_postgres-data`` and the media files are stored in the file system in ``data/media``.
Then you can update the project e. g. by changing the requirements and settings. Finally you can rebuild the web image
and start the server again:

.. code-block:: bash

  docker compose build web
  docker compose up -d

Creating pages
==============

The management command ``./manage.py create_pages`` creates an (empty) page tree of well-nested 19166 pages.
Run repeatedly to create more pages.
