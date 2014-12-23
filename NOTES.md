Concept
-------

Rewrite the platform powering the crowdsupply.com site in a new codebase, free
from links to scrappy / Cart Logic.

Maintainability is an extreme priority, and no new customer-facing features
should be introduced, except as essentially accidental byproducts of the
rewrite.

Until the platform takes over running the live site, this repo should also
serve to maintain the script(s) to migrate data from the old site.


Workflows / Model
-----------------

### Homepage Management

Should there be an admin tool for managing homepage state? This might be more
tricky than it's worth, but it would be really convenient to be able to
schedule changes in advance.

### Browse Page(s) Management

Mostly we're just talking about ordering and listing here. I think listing
works fine with the listed/unlisted toggle. Ordering could be improved for
sure.

### Project State

There are a lot of disparate states that aren't well encapsulated now.

- Prelaunch
- Project suspensions
- Crowdfunding
- Pre-order / In-stock (which should probably be combined, and the status made
  per pledge level instead)
- Should we support back-orders differently from just 'out of stock'? This gets
  messy.

Viewing and managing the content at different states could be improved too,
perhaps:

- Better UX for project creators and admins to view different states in advance
- Separate fields for body content in different stages?

I think it would be great if there was an sub navbar of some sorts on project
pages for admin users and project creators that made it easy to view different
states, and anticipated possible future self-serve editing interfaces.

A big problem right now is the management of whether or not a project is 'live'
prior to the launch date, and the need to specify a start/end time before
anything works.

### Order / Line Item State

The Cart Logic order and cart item states are only a rough match for the
actualities of Crowd Supply. States needed for things like:

- Project failed
- Payment failed, on hold
- Payment failed, no response
- Project suspended
... (try to enumerate other states here)

Here are existing payment states::

    available_payment_statuses = [
        ('unset', 'Unset'),
        ('prefunding', 'Project is not funded yet'),
        ('unfunded', 'Project did not meet funding goal'),
        ('unpaid', 'Item unpaid'),
        ('paid', 'Item paid'),
        ('cancelled', 'Order cancelled'),
        ('failed', 'Payment failed, awaiting resolution'),
        ('dead', 'Payment failed, order is closed'),
    ]

Maybe we should have separate shipping / inventory tracking states::

    available_shipping_statuses = [
        ('unset', 'Unset'),
        # XXX fill in here
    ]

### Custom Descriptors for Payments

If we're designing around only Stripe, we can use a custom descriptor that's
project-based.

### Measurement of Delivery Dates

We definitely want to be able to measure the on-time delivery rate of projects,
and see a queue of stuff like 'overdue orders'.

A 'project report card' could be good too.

### Better Account Page (as in the 'My Account' page)

The current page makes it very difficult to figure out your order status.

### Production Scheduling Model

- We show users the best current guess of the expected ship date for a pledge
  level if ordered now.
- We capture and preserve the date that was promised to an individual backer
  for all eternity.
- We anticipate the need for a delivery date to be moved back as more qty is
  consumed, based on a pre-planned table.

Plan:

- Use a PledgeBatch table
- On a Pledge line item, track the batch_id AND the original expected delivery
  date. Never change the original expected delivery date.
- Have an admin interface that lets you update the current expected delivery
  date of the batch, and add new batches to the end of the table.


Platform
--------

- Pyramid
- sqlalchemy
- gimlet
- manhattan for analytics / possible AB testing (this can be added later)
- pyramid_frontend for templating/theme/frontend
- pyramid_es with Elasticsearch
- pyramid_uniform for form validation?
- pyramid_cron for tasks
- pyramid_mailer for email
- alembic

Webserver
---------

- nginx
- uwsgi


Deployment
----------

- ansible


New Theme
---------

Since the theme needs to be somewhat re-implemented anyways, we may as well fix
a few things.

- Use bootstrap 3.3.1 but be prepared for the possibility that bootstrap 4 gets
introduced during dev, and switch to it if possible.
- Use require.js
- Try to avoid direct use of jquery?
