Jupyter cron
============

Simple clock/cron process that monitors a specific directory and run jobs based on its filename.

Currently filename with this pattern is supported:

(every X at time) where

**X** is ['day', 'monday', 'tuesday', 'wednesday','thursday', 'friday','saturday','sunday']

**time** is either in short form without minutes like 5PM or long form with minutes, 5:00PM


For example:

**notebooks/generate_model (every day at 5pm).ipynb**  will trigger `jupyter nbconvert` to run every day at 5pm.

**scripts/gen (every monday at 12pm).py** will trigger `python scripts/gen....py` to run.


Features
--------

- Simple to use
- Integrates well with Jupyter
- Tested on Python 3.6

Usage
-----

.. code-block:: bash

   usage: jupyter-cron [-h] [-d] glob

   Scans for file to run on a schedule based on its name

   positional arguments:
     glob             specify glob to search eg. test/**/*.ipynb

   optional arguments:
     -h, --help       show this help message and exit
     -d, --daemonize  daemonize the process

Meta
----

Quoc Le - `@realQuoc <https://twitter.com/realQuoc>`_ - quocble@gmail.com

Distributed under the MIT license. See ``LICENSE.txt`` for more information.

https://github.com/quocble/jupyter-cron
