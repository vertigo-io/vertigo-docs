# Text Input

Entering text in a management application is fairly common.
This type of input is used when the information in question cannot be standardized and therefore must be chosen freely by the user rather than selected from a pre-established list.

A text input is thus a free-form entry by the user. However, this does not mean it is free from controls.
We have selected three types of text input:

- single-line input
- multi-line input
- input in a rich-text editor (WYSIWYG)

The applicable controls can vary widely, but some examples include:

- maximum length
- minimum length
- imposed format (uppercase, lowercase, regular expression...)
- forbidden characters

These fields support copy/paste.

# Best Practices

- Single-line input should be the default choice
- When using multi-line input, provide a sufficient number of lines relative to the expected amount of information. (3-4 lines for a comments area, ~10 lines for more substantial input)
- Use the rich-text editor only when truly necessary, as its storage structure makes the information more difficult to process
- When a format must be followed and it is not trivial, provide the user with the rules to follow (via an input mask, a placeholder, or a "hint")
- When you want to give access to text information for reading, prefer using the component in "view" mode rather than the "edit" mode component set to disabled.
- When an HTML5 natively supported option exists for your need, always prefer it over custom code or a function provided by the component library, in order to improve the security and compatibility of your application.


# Design & Try me

<iframe src="/vertigo-docs/design-system/iframes/molecules/text-input.html" height="1000px" scrolling="no" style="border:none;" ></iframe>