Admin Human Interface Guide - a.k.a. Das Interface Rules
========================================================

Things with ``????`` are suggestions for further discussion.

Links & Buttons
---------------

* Buttons for actions, links for navigation
* Navigation outside the admin interface (e.g. view public page) should be considered an action, and use a button
* Button colors:
    * **Red** deletes data
    * **Blue** creates or modifies data
    * **Green** for starting a background process (like processing a queue) - would be rarely used
    * **Grey** for everything else
* Link are always **blue**
* Don't use blue for something that is not a link
* When a link is used to show additional hidden data, the "shown data" should be slightly greyed, to indicate a visual difference between it and the previously-shown data. This makes it easier for the user to tell what was "just shown".

Headers & Legends
-----------------

* Legends for areas within a form
* Table headers for, duh, tables
* ``????`` Don't use whole-page headers, use the HTML title or contextual admin instead

Tables
------

* Filter forms, pagers, and download links should be visually associated with the table they are affecting
* Sortable headers are **blue** when they go to a new page, **yellow** when they sort with javascript
* When row highlighting is added in a zebra striped table, zebra stripe the highlights too
* Row highlights colors:
    * **Orange** to indicate a warning state (e.g. pending, uncaptured, out of stock)

Confirmations & Flashes
-----------------------

* Always confirm deletes with a modal
* Flash colors:
    * Red means the last action failed or something is wrong which requires immediate attention
    * Yellow means something could be wrong or points out unusual states
    * Green means the last action succeeded
    * Light blue for everything else
* When a flash is shown which suggests an additional next step, use a confirmation flash ("block messages")

Form Fields
-----------

* Don't persist data without clicking a Save button
* One Update / Save button per page, **no exceptions**
* Collections for small lists which do not require additional data should use list of checkboxes (e.g. site associations)
* Collections for medium to large lists which do not require additional data should use multiselect (e.g. roles)
* Collections for lists which require additional data should use association table plus search (e.g. images)
* Prefixed / suffixed fields:
    * **$** prefix for currency
    * **@** prefix for email addresses
    * **%** suffix for percentages
    * **px** suffix for pixels
* Edit forms:
    * Include created/updated time and authors (when available) in top right
    * Include 'Edit ____' header with description of object
    * Save and Cancel dialog
    * Highlight changed fields
* Validation errors:
    * Highlight error fields
    * Show flash error

Dates & Times
-------------

* Always show time/date with timezone
* Date entry should include time where possible (e.g. make it clear when something is timed at 12:01am, 11:59pm, etc)
