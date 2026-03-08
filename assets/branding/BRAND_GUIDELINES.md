# Prism Brand Guidelines

**Tagline:** *"Refract complexity into clarity"*

---

## Logo Concept

```
     /\
    /  \
   /____\
  /\    /\
 /  \  /  \
/____\/____\
   PRISM
```

**Full ASCII Logo:**
```
        ╱╲
       ╱  ╲
      ╱____╲
     ╱╲    ╱╲
    ╱  ╲  ╱  ╲
   ╱____╲╱____╲
   
   💎  P R I S M
   
   Refract complexity
     into clarity
```

---

## Color Palette

### Primary Colors
```yaml
primary:
  prism_blue: "#4A90E2"      # Bright, clear blue
  prism_purple: "#9B59B6"    # Rich purple
  prism_cyan: "#1ABC9C"      # Vibrant cyan

secondary:
  deep_indigo: "#2C3E50"     # Dark backgrounds
  light_gray: "#ECF0F1"      # Light backgrounds
  white: "#FFFFFF"           # Text on dark
  
accent:
  rainbow_gradient:
    - "#FF6B6B"  # Red
    - "#FFA500"  # Orange  
    - "#FFD93D"  # Yellow
    - "#6BCF7F"  # Green
    - "#4A90E2"  # Blue
    - "#9B59B6"  # Purple
```

### Usage
- **Headers/Titles:** `prism_blue` (#4A90E2)
- **Code/Terminal:** `deep_indigo` (#2C3E50)
- **Success:** `prism_cyan` (#1ABC9C)
- **Accents:** Rainbow gradient for logo/branding
- **Backgrounds:** `light_gray` (light mode), `deep_indigo` (dark mode)

---

## Typography

### Primary Font
**JetBrains Mono** (monospace, developer-friendly)
- Headers: Bold
- Body: Regular
- Code: Regular

### Fallbacks
- `'JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', monospace`

---

## Visual Identity

### The Prism Metaphor

**White light (complexity) → Prism → Rainbow (clarity)**

- Complex setup → Prism → Organized, beautiful environment
- Many tools → Prism → Single command
- Chaos → Prism → Structure

### Logo Variations

1. **Full Logo** - Geometric prism + wordmark + tagline
2. **Icon Only** - Geometric prism (for favicons, small spaces)
3. **Wordmark** - "PRISM" text with prism icon
4. **Minimal** - Just 💎 emoji (for CLI)

---

## CLI Branding

### Command Prompt
```bash
💎 prism init
💎 prism install my-company
💎 prism list
💎 prism refract  # Special command for package creation
```

### Terminal Output Style
```
╭─────────────────────────╮
│  💎  P R I S M      │
│                         │
│  Refract complexity      │
│  into clarity            │
╰─────────────────────────╯

✔ Installing tools...
✔ Configuring git...
✔ Setting up workspace...

🌈 Environment ready!
```

---

## Emoji Usage

- 💎 Primary logo emoji
- ✨ Clarity, refraction, light effects
- 🌈 Rainbow (output of prism)
- 🔬 Precision, science
- 💡 Ideas, illumination
- ✔ Success
- ❌ Error
- ⚠️ Warning

---

## Web/Documentation

### Header Example
```html
<header style="background: linear-gradient(135deg, #4A90E2, #9B59B6);">
  <h1>💎 PRISM</h1>
  <p>Refract complexity into clarity</p>
</header>
```

### Feature Cards
Use gradient borders with rainbow colors:
```css
.feature-card {
  border: 2px solid transparent;
  background: linear-gradient(white, white) padding-box,
              linear-gradient(135deg, #FF6B6B, #9B59B6) border-box;
}
```

---

## Voice & Tone

### Personality
- **Clear**: No jargon, simple explanations
- **Scientific**: Precision, accuracy
- **Helpful**: Guiding, not commanding
- **Modern**: Clean, minimalist

### Language
- Use "refract" instead of "configure"
- Use "clarity" instead of "simplicity"
- Use "spectrum" for options/choices
- Use "illuminate" for documentation

### Example Copy
- ❌ "Configure your development environment"
- ✔ "Refract chaos into clarity"

- ❌ "Install multiple tools"
- ✔ "One command, complete spectrum of tools"

---

## File Structure

```
assets/
├── branding/
│   ├── BRAND_GUIDELINES.md    # This file
│   ├── logo.svg              # Full color logo
│   ├── logo-dark.svg         # Dark mode variant
│   ├── icon.svg              # Icon only
│   ├── wordmark.svg          # Text + icon
│   └── colors.yaml           # Color definitions
│
├── icons/
│   ├── favicon.ico
│   ├── apple-touch-icon.png
│   └── android-chrome-512x512.png
│
└── screenshots/
    ├── cli-demo.gif
    ├── installation.png
    └── web-ui.png
```

---

## Package Asset Support

Packages can include their own assets:

```yaml
# package.yaml
package:
  name: "my-company"
  
  assets:
    logo: "assets/logo.png"
    icon: "assets/icon.svg"
    banner: "assets/banner.jpg"
    
  branding:
    primary_color: "#0053e2"
    secondary_color: "#ffc220"
    logo_url: "https://company.com/logo.svg"
```

Assets are installed to:
```
~/.prism/assets/[package-name]/
```

And referenced in UIs:
```python
logo_path = Path.home() / ".prism" / "assets" / package_name / "logo.png"
```

---

**Created:** 2025-03-05  
**By:** William Anderson  
**Version:** 1.0  
