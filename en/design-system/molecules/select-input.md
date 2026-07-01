# Select Input

Select components allow entering a value from a list of possible choices.
User input is then strictly constrained.

This type of select component is used when choices are mutually exclusive and the user should select only one value from the proposed alternatives.

We have selected three types of selection:

- radio buttons
- dropdown list
- autocomplete


All these selection methods can be used with keyboard-only input to improve accessibility.
Good to know: the dropdown list component allows the user to type the first letters to navigate the list more quickly.

# Best Practices

The main selection criterion for choosing one component over another is the volume of possible options.
- For a small number of options (<7): prefer radio buttons because they allow viewing all values
- For a moderate number of options (>7 and <100): prefer the dropdown list because it is the easiest to use and improves screen density
- For a very large number of options (>100): prefer autocomplete because it is the only one that can ensure good performance. This component natively supports "starts with" search on a large volume of data
- The order of options must be reproducible and understandable. We prefer alphabetical order.
- If there is no particular reason to use a "radio" list, prefer the dropdown list, even with a small number of options, to densify information.


# Design & Try me

<iframe src="/vertigo-docs/design-system/iframes/molecules/select-input.html" height="700px" scrolling="no" style="border:none;" ></iframe>