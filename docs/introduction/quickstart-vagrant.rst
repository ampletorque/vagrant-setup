Quick Start with Vagrant
========================

Install VirtualBox and Vagrant
------------------------------

Install VirtualBox and Vagrant for your platform:

* `VirtualBox <https://www.virtualbox.org>`_
* `Vagrant <https://www.vagrantup.com>`_


Checkout Zaphod to the Host Computer
------------------------------------

Clone the repo::

    $ git clone git@github.com:crowdsupply/zaphod.git

Start a new Vagrant VM and provision it with Zaphod::

    $ vagrant up

View the website in a browser at http://192.168.3.100.

Development and Deployment
--------------------------

To edit the source, you can log into this vagrant VM::

    $ vagrant ssh

    ...

    $ cd /var/sw/zaphod

Restart the server with::

    $ sudo restart uwsgi
