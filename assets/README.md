# Images

The pictures in the main README. They are under CC BY 4.0 like the rest of the content
(`LICENSE-CONTENT.md`).

- `banner.png`, `loop.png`: drawn with Pillow at twice the size they are shown at.
- `demo.gif`: a terminal recording drawn from real `coach` CLI output for an invented client
  (`coach macros`, `coach strength progress --exercise squat`, then
  `coach profile set screening.cardiac_symptoms true` and the same progression again). Some JSON
  fields are left out, marked with `…`.
- `menu-pdf.png`: pages 1, 2 and 4 of a three-day menu exported with `coach mealplan export` for
  an invented client (the week with the first cards, more recipe and amount cards, the shopping
  list; page 3 holds the last recipe), rendered with `pdftoppm -r 150` and laid side by side with
  Pillow.

No personal data went into any of them. When a command's output changes, re-record the demo from
a fresh data folder with an invented client rather than editing the image.
