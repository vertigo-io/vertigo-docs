# Form

In management applications, data play a very important role.
By extension, input forms are very numerous in this type of application. They must allow the entry of information that is:

- reliable
- fluid and ergonomic
- consistent

To achieve these objectives, we have made certain structural choices.
First, all input components (molecules) share common features: a fixed label, error message handling, input assistance, and two rendering modes: an edit mode and a view mode.

The ability of each molecule to display in both rendering modes ensures maximum consistency between input pages and view pages, perfectly guiding the user through their journey.

Furthermore, all the components we have selected can operate using only the keyboard for improved accessibility.

# Best Practices

- Always place fields that are functionally close to each other near one another
- Prioritize global server-side controls, as these are the only ones capable of guaranteeing application integrity. Use client-side surface controls as a complement.
- Try to maximize display density to spare your users unnecessary "scrolling."
- The label should be short and precise, always on a single line
- Prefer short input hints, on a single line, or place them outside the input field
- Always indicate whether a field is mandatory (this is handled automatically in Vertigo, consistent with the model)

# Design & Try me

<iframe src="/vertigo-docs/en/design-system/iframes/molecules/form.html" height="1000px" scrolling="no" style="border:none;" ></iframe>