Quick Start Deploying to Production
========================

Checkout Zaphod to the Host Computer
------------------------------------

Clone the repo::

    $ git clone git@github.com:crowdsupply/zaphod.git

Development
-----------

Make an commit changes, e.g.::

    $ git commit -a -m "Updated homepage tiles."
    $ git push origin master

Deployment
----------

Run the Ansible playbook::

    $ cd <path to your zaphod checkout>/site/ansible
    $ ansible-playbook -i production deploy.yml
