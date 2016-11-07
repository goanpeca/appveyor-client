appveyor-client
===============

Build status
------------
|travis status| |appveyor status| |circleci status| |quantified code| |scrutinizer|

Project information
-------------------
|license| |pypi version|

.. |travis status| image:: https://travis-ci.org/goanpeca/appveyor-client.svg?branch=master
   :target: https://travis-ci.org/goanpeca/appveyor-client
   :alt: Travis-CI build status
.. |appveyor status| image:: https://ci.appveyor.com/api/projects/status/mgv5gnstlxv718xk?svg=true
   :target: https://ci.appveyor.com/project/goanpeca/appveyor-client
   :alt: Appveyor build status
.. |circleci status| image:: https://circleci.com/gh/goanpeca/appveyor-client/tree/master.svg?style=shield
   :target: https://circleci.com/gh/goanpeca/appveyor-client/tree/master
   :alt: Circle-CI build status
.. |quantified code| image:: https://www.quantifiedcode.com/api/v1/project/cc20fe74549746108607476699d2d7ec/badge.svg
   :target: https://www.quantifiedcode.com/app/project/cc20fe74549746108607476699d2d7ec
   :alt: Quantified Code issues
.. |scrutinizer| image:: https://scrutinizer-ci.com/g/goanpeca/appveyor-client/badges/quality-score.png?b=master
   :target: https://scrutinizer-ci.com/g/goanpeca/appveyor-client/?branch=master
   :alt: Scrutinizer Code Quality
.. |license| image:: https://img.shields.io/pypi/l/appveyor-client.svg
   :target: LICENSE.txt
   :alt: License
.. |pypi version| image:: https://img.shields.io/pypi/v/appveyor-client.svg
   :target: https://pypi.python.org/pypi/appveyor-client/
   :alt: Latest PyPI version

Description
-----------
Simple python interface to the Appveyor restful api.

Usage
-----

::

  from appveyor_client import AppveyorClient
  client = AppveyorClient('{appveyor_token}')

  # Get list of projects
  projects = client.projects.get()

  # Get list of projects builds
  builds = client.projects.history('goanpeca', 'appveyor-client')


Installation
------------

Using pip

::

    pip install appveyor-client

Using conda

::

    conda install appveyor-client -c conda-forge
