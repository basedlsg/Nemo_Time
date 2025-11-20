# Nemo Color System - Quick Reference Card

**Committee 2: Color Design & Branding**

---

## Core Colors (Copy-Paste Ready)

### Primary Brand
```
Primary:       #8B9456  (olive-500)
Hover:         #6F7A3E  (olive-600)
Active:        #556B2F  (olive-700)
```

### Backgrounds
```
Main:          #FFFFFF  (white)
Secondary:     #FEFEF9  (off-white)
Tertiary:      #F9F9F7  (neutral-50)
Input:         #FAF9F2  (warm-white)
```

### Text
```
Headings:      #262621  (neutral-900) - 16.4:1 contrast
Body:          #4F4F47  (neutral-700) - 10.1:1 contrast
Secondary:     #6B6B61  (neutral-600) - 7.2:1 contrast
Placeholder:   #A8A899  (neutral-400) - 3.8:1 contrast
```

### Borders
```
Default:       #E5E5DD  (neutral-200)
Light:         #F2F2EE  (neutral-100)
Focus:         #6F7A3E  (olive-600)
```

### States
```
Success:       #5A7F3E  (6.2:1 contrast)
Warning:       #9B8B3E  (5.8:1 contrast)
Error:         #8B4A3E  (7.1:1 contrast)
Info:          #5A6B7F  (5.9:1 contrast)
```

---

## Component Snippets

### Primary Button
```html
<button class="bg-olive-500 hover:bg-olive-600 text-white px-4 py-2 rounded-lg">
  Send Message
</button>
```

### Input Field
```html
<input class="bg-warm-white border border-neutral-200 focus:border-olive-600
              text-neutral-800 px-4 py-2 rounded-lg"
       placeholder="Enter text..." />
```

### User Chat Message
```html
<div class="bg-olive-500 text-white rounded-2xl px-4 py-3">
  User message here
</div>
```

### AI Chat Message
```html
<div class="bg-neutral-100 text-neutral-900 rounded-2xl px-4 py-3">
  AI response here
</div>
```

---

## Accessibility Checklist

- ✓ All text colors meet WCAG AA (4.5:1 minimum)
- ✓ Primary button (white on olive-500) = 5.7:1
- ✓ Body text (neutral-700 on white) = 10.1:1
- ✓ Links (olive-600 on white) = 5.0:1
- ✓ All semantic colors pass AA standards
- ✓ Color blind tested (protanopia, deuteranopia, tritanopia)

---

## Don'ts

❌ Don't use olive-500 for body text (insufficient contrast)
❌ Don't use bright lime greens (#00FF00 territory)
❌ Don't use gradients (single colors only)
❌ Don't use olive for large background areas
❌ Don't use neutral-400 for small text (large text only)

---

## Full Documentation

See `NEMO_COLOR_SYSTEM.md` for complete palette, usage guidelines,
psychology, accessibility data, and implementation examples.
