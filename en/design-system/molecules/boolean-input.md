# Boolean Input

A boolean input represents a binary true or false value.
For these types of data, it is very important to choose a rendering method that is not ambiguous for users.

Therefore, we chose to prioritize a single way of entering this type of information via a checkbox.
This choice is motivated by three main reasons:

- it's the historical choice of the web, the one that will least disorient users regardless of their computer skills
- it's the least ambiguous and therefore the most accessible
- it works identically on mobile and desktop via a tap/click

# Best Practices

- A boolean value should always be pre-initialized. Some programming languages allow other states (for example using null). We strongly advise against this practice.
- When a distinction must be made between an unsaved value and a null value, prefer another unambiguous selection component, such as a "radio"


# Design & Try me

<iframe src="/vertigo-docs/design-system/iframes/molecules/boolean-input.html" height="300px" scrolling="no" style="border:none;" ></iframe>