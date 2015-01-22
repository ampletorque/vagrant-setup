Ansible To-Do List
==================

- Configure MySQL to bind only to loopback
- Configure MySQL for performance??

- Set Pyramid log file permissions to group-writeable so that deploy user can
  run Pyramid scripts.

- Provisioning shouldn't fail if /var/certs is not available locally.

- Data population should try to fetch original images from blofeld, rather than
  the host running Ansible.



Future To-Do
============

- Make deployment and provisioning playbooks work for production OR staging,
  and pass environment context to Pyramid config.

- Write a new playbook for syncing data from a deployed server to the host
  running Ansible.
