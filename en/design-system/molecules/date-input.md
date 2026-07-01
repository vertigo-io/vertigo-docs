# Date Input

Entering a date may seem trivial at first glance, but it can prove very complex if the related concepts are not well understood.
Let us try to present this concisely.
There are two main families of data that provide temporal information:

- dates: which come from a calendar. A calendar is a logical and human representation of time that depends (among other things) on a spatial location.
- timestamps (or instants in English): which universally represent a point on the time scale

It is possible to "project" a timestamp into a date by adding a timezone.
This projection is always a business choice: the choice of which timezone to use can be the timezone of the user viewing the data or information provided by the business context.

User input occurs at two levels of precision:

- day
- minute

Second-level precision or lower will generally only be necessary for viewing.

Therefore, we have selected two temporal data input components:

- date: which allows entering a date in day/month/year format
- datetime: which allows entering a time and date in day/month/year hour:minutes format

These two components allow input through two complementary methods:

- via text input for more experienced users or when the date is known in advance
- via a selection widget

When it is necessary from a business standpoint to input timezone information, we prefer to enter this information in a separate field.

These various choices allow managing temporal information consistently and reliably throughout the chain, from input to visualization, including transfer and storage.

# Best Practices

- By default, a date (day precision) is timezone-less and should be considered local
- By default, a datetime (minute precision) is timezone-less and should be considered local
- When a datetime (minute precision) must be zoned, the server performs the conversion based on business logic.
- The user interface manipulates the timezone concept exclusively in specific fields independent of the date and datetime components


# Design & Try me

<iframe src="/vertigo-docs/en/design-system/iframes/molecules/date-input.html" height="700px" scrolling="no" style="border:none;" ></iframe>