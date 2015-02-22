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

Change 'delivery date' language to 'ship date'!

### User / Account Handling

Prevent accounts from being created with duplicate email addresses, with a unique constraint on User.email. If an order is placed by a non-logged in user with an email address that is not 'taken', create an account for that email. If the email address is already taken, do not associate the order with an account. If the email is not taken, create an account for that email/order.

In a logged-in user's account page, show a form which allows associating an orphan order by order ID and postal code.

If possible, provide alternate means of associating orders easily, but think very carefully about the security implications of doing so.

### Better Account Page (as in the 'My Account' page)

The current page makes it very difficult to figure out your order status.

### Production Scheduling Model

- We show users the best current guess of the expected ship date for a pledge
  level if ordered right now.
- We capture and preserve the date that was promised to an individual backer
  for all eternity (associated with that order line item).
- We anticipate the need for a delivery date to be moved back automatically as
  more qty is consumed, based on a pre-planned table.

Plan:

- Use a PledgeBatch table like we have now.
- On a Pledge line item, track the batch_id AND the original expected delivery
  date. Never change the original expected delivery date on the corresponding
  line item.
- Have an admin interface that lets you update the current expected delivery
  date of the batch, and add new batches to the end of the table.


### Model Cleanup

- Ensure consistent table naming.
- Be consistent about using either ``_time`` or ``_date`` as the suffix for
  DATETIME columns, but not both!


### Frontend Cleanup

- Use .box-shadow() mixin instead of box-shadow rule directly
- Switch to SVG logo??
- Styling for breadcrumbs
- Styleguide info for tiles
- Use sticky sidebar on styleguide
- Introduce an @hr-color variable and add it to the styleguide
- Standardize colors for grey / lightened text, add vars, add to styleguide
