# Numeric Input

There are several ways to enter and represent numeric formats on the web.
This section is not intended to be exhaustive nor to address data visualization issues (Dataviz, Charts, etc.)

We propose different methods that allow both the input and viewing of single numeric data values.
There are three:

- via a single-line text field
- via a virtual rotary knob
- via a virtual linear slider

All three methods allow controlling the minimum and maximum allowed values as well as the required precision.
When entering a numeric value via text input, Vertigo will automatically verify the validity of the value and display an error message if necessary.

# Best Practices

- When entering numeric data, it may be important to specify the expected unit
- Knobs always require the definition of a minimum and maximum value
- When inputting via a virtual knob, always ensure that the precision is compatible with the input capability. If the adjustment is too fine, some values will not be enterable; conversely, too coarse an adjustment will confuse the user. By default, Vertigo configures these knobs based on min and max bounds so that 200 values are selectable. This can obviously be overridden.


# Design & Try me

<iframe src="/vertigo-docs/design-system/iframes/molecules/numeric-input.html" height="1000px" scrolling="no" style="border:none;" ></iframe>