# Collections

Displaying collections of elements is very common.

We have selected three methods for visualizing collections:

- as a list of [cards](design-system/organismes/cards.md)
- as a list of [lines](design-system/organismes/items.md)
- as a [table](design-system/organismes/table.md)

These three visualization methods share common sorting and pagination functions.

We made the structural choice to prioritize:

- server-side sorting: because it is the only way to ensure reliable and exhaustive sorting on large collections
- client-side pagination on a list of a maximum of 250 elements: because it is the only method that allows very fast and smooth navigation.

When the collection in question is small (<250 elements), client-side sorting is possible.

These design choices also stem from our observation that users rarely navigate beyond the 100th element, and even when they do, it costs them a lot of time. We therefore prefer to provide users with tools to pre-filter elements, sort by relevance and characteristics, and ensure that the information the user is looking for appears on the first page 90% of the time.
This is made possible in particular by the very simple use of faceted full-text search.


# Best Practices

- Always prefer server-side sorting, the only reliable sort
- Never return more than 250 elements to the user; additional elements will not be read and cause performance issues
- With card display, prefer showing an additional page via a "See more" type button
- With list or table display, prefer classic pagination by "page number" and/or by "previous page"/"next page" buttons
- At the top of the list, indicate the total number of elements matching the entered criteria


# Design

You can find the various designs here: [cards](design-system/organismes/cards.md), [lines](design-system/organismes/items.md), [table](design-system/organismes/table.md)