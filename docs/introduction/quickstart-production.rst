Quick Start Deploying to Production
========================

Host Computer Setup
------------------------------------

Clone the repo::

    $ git clone git@github.com:crowdsupply/zaphod.git

Enable SSH agent forwarding, if it's not already enabled. `This GitHub guide <https://developer.github.com/guides/using-ssh-agent-forwarding/>`_ is a good reference for what's involved.

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
