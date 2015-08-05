Project
=======

Projects are a grouping of similar Products, launched in a cohesive "campaign".

They can go through a number of states:

.. graphviz::

    digraph finite_state_machine {
        rankdir=TB;

        node [shape = box];

        node [penwidth = 1];

        Prelaunch -> Crowdfunding;

        Crowdfunding -> Suspended;
        Crowdfunding -> Failed;
        Crowdfunding -> Funded;
        Crowdfunding -> Available;

        Funded -> Available;

        Available -> Funded;
    }

Projects will typically start in either the 'Prelaunch' or 'Crowdfunding'
state. The present state of a Project is determined on-the-fly and not returned
as the ``Project.status`` property, and is not stored in the DB. Status may be
time-variant, because a crowdfunding campaign will have an "end time", after
which the project shifts into an alternate state.


Project API
-----------

.. automodule:: zaphod.model.project
    :members:
    :undoc-members:
