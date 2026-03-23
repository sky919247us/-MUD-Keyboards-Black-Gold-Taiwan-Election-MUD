```markdown
# Design System Document: Cyber-Political Interface

## 1. Overview & Creative North Star: "The Digital War Room"
The Creative North Star for this system is **"The Digital War Room."** This isn't just a game; it is a high-stakes simulation of Taiwanese political maneuvering. We are moving away from the friendly, rounded "app" aesthetic. Instead, we embrace **Brutalist Information Architecture**: a gritty, data-dense environment that feels like a leaked intelligence terminal.

The design breaks the standard mobile template through **intentional asymmetry** and **monolithic layering**. By utilizing hard edges (0px border radius) and high-contrast typography, we create a UI that feels urgent, authoritative, and unapologetically modern-Taiwanese. 

---

## 2. Colors: High-Voltage Surveillance
The palette is rooted in the "Black Gold" (political corruption) aesthetic—deep, charcoal voids punctured by neon indicators of progress and the violent red of a political crisis.

### Color Tokens
*   **Primary (`#8eff71`):** "Neon Progress." Use for successful hacks, rising poll numbers, and positive momentum.
*   **Secondary (`#99b8fe`):** "Traditional Blue." Represents establishment power, stability, and institutional data.
*   **Tertiary (`#ff7073`):** "Crisis Red." Reserved for scandals, smear campaigns, and critical errors.
*   **Background (`#0c0e11`):** The "Void." A deep charcoal that provides the canvas for the glowing terminal.

### The "No-Line" Rule
**Prohibit 1px solid borders for sectioning.** Boundaries must be defined through background shifts. For example, a `surface-container-low` section should sit against the `background` to create a logical break. Use the `Spacing Scale` (e.g., `spacing-8`) to let the negative space act as the divider.

### Signature Textures
To avoid a "flat" look, apply a subtle **Scanline Overlay** (a 2px repeating linear gradient) at 5% opacity over `surface-container-highest` elements to mimic a CRT monitor. Use a gradient transition from `primary` to `primary-container` for major action buttons to give them a "charged" kinetic energy.

---

## 3. Typography: The Bold Mandate
We utilize **Noto Sans TC** (Traditional Chinese) for its structural integrity and **Space Grotesk** for Latin alphanumerics to lean into the "tech-noir" vibe.

*   **Display-LG (3.5rem):** Used for "Election Day" countdowns and major victory/defeat screens.
*   **Headline-MD (1.75rem):** For news headlines and legislative bills.
*   **Body-MD (0.875rem):** The workhorse for MUD-style text logs. This must be highly legible against the dark background.
*   **Label-SM (0.6875rem):** Used for "Metadata"—timestamping political leaks or displaying candidate stats.

**Hierarchy Note:** Use `on-surface-variant` (grey) for flavor text and `primary` (neon green) for actionable keywords within text blocks to guide the player's eye through the "data noise."

---

## 4. Elevation & Depth: Tonal Layering
In this system, depth is not "shadow"; depth is "signal strength." We use a **0px Roundedness Scale**—everything is sharp, clinical, and aggressive.

*   **The Layering Principle:** Stack `surface-container-lowest` (000000) for the main terminal background, and use `surface-container-high` for interactive dialogue modules. This creates a "recessed" or "elevated" look without a single drop shadow.
*   **Glassmorphism:** For floating HUD elements (like a "Current Polls" overlay), use `surface` at 60% opacity with a `backdrop-filter: blur(12px)`. This suggests a high-tech "heads-up display" over the gritty street-level data.
*   **The Ghost Border:** If a distinction is critical (e.g., a focused input field), use `outline-variant` at 20% opacity. Never use 100% opaque lines.

---

## 5. Components: The Political Toolkit

### Terminal Text Boxes
*   **Style:** `surface-container-lowest` background. 
*   **Interaction:** Text should appear via a "typewriter" stagger effect. Use `primary` for the cursor `_`.
*   **Spacing:** Use `spacing-4` internal padding to ensure text doesn't hit the sharp edges.

### Action Buttons
*   **Primary:** Background: `primary` (`#8eff71`), Text: `on-primary` (`#0d6100`). High contrast, 0px radius.
*   **Secondary:** Ghost style. No background, `outline` token at 40% opacity, `secondary` text.
*   **State:** On `active`, the button should "glitch"—shifting 2px to the left and changing background to `primary-dim`.

### Lists & Feed Items
*   **Constraint:** **Strictly forbid divider lines.** 
*   **Implementation:** Separate news feed items using `surface-container-low` and `surface-container-highest` alternating blocks, or simply use `spacing-6` vertical gaps.

### Pixel-Art Icons
*   **Guideline:** Icons (Representing "Coalition," "Bribe," "Speech") should be 1-bit style pixel art but colored with the `secondary` or `tertiary` tokens. They should be sized to exactly match the `headline-sm` cap height.

### Input Fields
*   **Style:** Underline only (using `outline` token at 50%). No four-sided boxes.
*   **Error State:** The underline shifts to `error` (`#ff7351`) with a subtle `error-container` glow behind the text.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** embrace "Data Density." It’s okay to have a lot of text if the hierarchy (via typography scale) is clear.
*   **Do** use the `0.1rem` (spacing-0.5) for micro-adjustments in "tech" details, like small corner accents.
*   **Do** treat the "Red" (`tertiary`) as a weapon. Use it sparingly so that when it appears, the player feels an immediate sense of "Crisis."

### Don’t:
*   **Don’t** use rounded corners. A 4px radius ruins the "Gritty Terminal" aesthetic.
*   **Don’t** use standard "Material Design" shadows. If you need lift, use a `surface-bright` background shift.
*   **Don’t** use "Soft Blue." Use our `secondary` (`#99b8fe`), which is colder and more clinical.
*   **Don’t** use dividers. If the UI feels cluttered, increase the spacing scale rather than adding a line.

---

## Director's Closing Note
This system should feel like a tool used by a political operative in a rain-slicked Taipei alleyway. It is cold, sharp, and efficient. Every pixel must feel like it’s serving the "Election Win," not just looking "pretty." Keep it grit-focused, keep it data-heavy, and keep it sharp.```