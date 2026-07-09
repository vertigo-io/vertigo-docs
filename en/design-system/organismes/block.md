# Block

To structure information in an application, it is very often useful to group together items that are related from a business standpoint and form a coherent whole.
Blocks are a good way to do this.
A block is composed of:

- a title
- an optional action area at the top right
- a content area

Different types of content can be placed in the designated area: for example, input or display fields, images, charts, etc.

# Best Practices

- The block title should be short and unambiguous
- Actions placed on a block must be contextual to the elements contained within the block and should be limited in number (<3).
- We strongly advise against using block actions to save modifications or switch to edit mode. Indeed, for security and integrity reasons, it is preferable for this switch to occur at the page level, because an edit page and a view page have entirely different technical structures (even if this is not visible to the end user). It is entirely possible to deviate from this rule in exceptional cases, but the impacts in terms of security, integrity loss, and associated development overhead must be taken into consideration.
- The block color should contrast with the application background and allow good readability of the content placed inside. We recommend white.


# Design & Try me

<iframe src="/vertigo-docs/en/design-system/iframes/organismes/block.html" height="300px" scrolling="no" style="border:none;" ></iframe>