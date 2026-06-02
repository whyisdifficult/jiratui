# Textual Framework

JiraTUI is built on [Textual](https://textual.textualize.io/), a Python framework for building terminal UIs. You don't
need to be a Textual expert to contribute, but understanding these core concepts will make development much smoother.

## Essential Concepts

**Widgets**: The building blocks of any Textual app. Widgets are reusable UI components (buttons, inputs, containers,
custom displays, etc.). When adding features to JiraTUI, you'll often extend existing widgets or create new ones.
[Learn more](https://textual.textualize.io/guide/widgets/).

**Screens**: A screen is the top-level container for a set of widgets. JiraTUI uses screens to manage different
views (e.g., creating work items, attaching files, etc.). Each screen handles its own layout and behavior.
[Learn more](https://textual.textualize.io/guide/screens/).

**Messages & Events**: Textual uses a message-passing system for communication between widgets. When a user interacts
with a widget (clicks a button, types text), it emits a message. Other widgets can handle these messages to update
state or trigger actions. [Learn more](https://textual.textualize.io/guide/events/).

**CSS Styling**: Textual supports CSS-like styling for layout, colors, and spacing. This keeps styling logic separate
from widget code and makes the codebase cleaner. [Learn more](https://textual.textualize.io/guide/CSS/).

**Keybindings**: Define keyboard shortcuts and their handlers within a widget or
screen. [Learn more](https://textual.textualize.io/guide/input/#bindings).

## Next Steps

Familiarize yourself with the [Textual tutorial](https://textual.textualize.io/tutorial/) before diving into the
codebase. Understanding message flow and widget lifecycles will save you debugging time.
