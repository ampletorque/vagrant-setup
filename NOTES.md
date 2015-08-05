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

### User / Account Handling

Prevent accounts from being created with duplicate email addresses, with a unique constraint on User.email.

If an order is placed by a logged-in user, just associate it with the account.

If an order is placed by a non-logged-in user, and the email already has an account, associate the order with the account, but don't log the user in or tell the web session user that the account already existed. Send an email with a link to reset the password.

If an order is placed by a non-logged-in user, and the email does not have an account, create an account and associate the order, but don't log the user in or tell the web session user that the account has been newly created. Send a welcome email with a link to set the password.
