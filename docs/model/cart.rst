Carts and Items
===============

A visitor's shopping cart on the site is represented by ``Cart`` and
``CartItem`` objects.

A Cart is simply a plain grouping of ``CartItem`` instances that correspond
to a particular session. Most important logic and state is item-specific.

Items go through the following states. "Final" states, after which the item
cannot transition into any other state, are outlined in bold.

.. graphviz::

    digraph finite_state_machine {
        rankdir=TB;

        node [shape = box];

        node [penwidth = 3];
        Failed Shipped Cancelled Abandoned;

        node [penwidth = 1];

        Unfunded -> "Payment unprocessed";
        Unfunded -> Failed;

        "Payment unprocessed" -> "Waiting for items";
        "Payment unprocessed" -> "Payment failed";

        "Payment failed" -> Abandoned;
        "Payment failed" -> "Waiting for items";
        "Payment failed" -> "In process";

        "Waiting for items" -> "In process";
        "In process" -> "Being packed";
        "Being packed" -> Shipped;

        Unfunded -> Cancelled;
        "Payment failed" -> Cancelled;
        "Payment unprocessed" -> Cancelled;
        "Waiting for items" -> Cancelled;
        "In process" -> Cancelled;
    }


The item status is persisted as the ``CartItem.status`` column.

Cart API
--------

.. automodule:: zaphod.model.cart
    :members:
    :undoc-members:
