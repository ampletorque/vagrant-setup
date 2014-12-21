CSS Style Guide
===============

* 4-space tabs, never ``\t``.
* Classes and IDs should be hyphen-seperated, lowercase, alphanumeric.
* Put spaces before ``{`` in rule declarations.
- One property per line.
* Put spaces after ``:`` in property declarations.
* Prefix page-specific selectors with a namespace, like ``product-cart-block``.
- For .less, indent each nested selector by 4 spaces.


A full example:

.. code-block:: css

    .product-table {
        tr {
            font-weight: bold;
            text-align: center;
            &.item-row {
                padding-top: 10px;
                padding-bottom: 10px;
            }
        }
        td:last-child {
            border-right: 1px solid #e7e7e7;
        }
    }


