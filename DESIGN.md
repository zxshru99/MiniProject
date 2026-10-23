# DESIGN.md — UI/UX Design Specification

**Project:** AgriAI Platform
**Version:** 1.0

---

## 1. Design Philosophy

- **Simple first:** Farmers are the primary users. Every screen must be usable on a mid-range Android phone.
- **Results-first layout:** Show prediction results prominently. Don't bury them.
- **Dark mode by default:** Easier to read outdoors in sunlight (farmers use phones outside).
- **Green/earth color palette:** Agriculture context. Not neon, not corporate blue.
- **No jargon:** Show "Your soil needs water now" not "VWC: 12.3% — CRITICAL_DRY state detected."

---

## 2. Color System

```css
/* Primary Palette */
--color-green-dark:   #1a3a2a;   /* backgrounds, sidebars */
--color-green-mid:    #2d6a4f;   /* buttons, headers */
--color-green-light:  #52b788;   /* highlights, success states */
--color-green-accent: #74c69d;   /* active states, hover */

/* Neutral */
--color-bg-dark:      #0f1f17;   /* page background (dark mode) */
--color-bg-card:      #1c2e22;   /* card backgrounds */
--color-text-primary: #e8f5e9;   /* main text */
--color-text-muted:   #a5c8a8;   /* secondary text */
--color-border:       #2d6a4f33; /* card borders */

/* Status Colors */
--color-dry:          #e76f51;   /* dry soil alert */
--color-moderate:     #f4a261;   /* moderate moisture */
--color-wet:          #52b788;   /* good moisture */
--color-saturated:    #264653;   /* oversaturated */

/* Data Visualization */
--chart-1: #52b788;
--chart-2: #f4a261;
--chart-3: #e76f51;
--chart-4: #457b9d;
--chart-5: #a8dadc;
```

---

## 3. Typography

```css
/* Use from Google Fonts */
font-family: 'Inter', sans-serif;   /* all body text */
font-family: 'Outfit', sans-serif;  /* headings only */

/* Scale */
--text-xs:   0.75rem;   /* 12px — labels, badges */
--text-sm:   0.875rem;  /* 14px — secondary info */
--text-base: 1rem;      /* 16px — body */
--text-lg:   1.125rem;  /* 18px — card titles */
--text-xl:   1.25rem;   /* 20px — section headers */
--text-2xl:  1.5rem;    /* 24px — page titles */
--text-3xl:  1.875rem;  /* 30px — hero numbers */
```

---

## 4. Pages & Screens

### 4.1 Auth Pages
**`/login`**
- Email + password fields
- "Forgot password?" link
- Link to register
- No social login (out of scope)

**`/register`**
- Full name, email, phone, password, confirm password
- Role selector: Farmer / Researcher (admin is set manually)

---

### 4.2 Farmer Portal — Dashboard (`/dashboard`)

**Layout:** Sidebar (desktop) / Bottom nav (mobile)

**Cards on dashboard:**
1. **"Last Analysis"** — shows most recent prediction result with soil type badge
2. **"Weather Today"** — temperature, humidity, rainfall for their primary field location
3. **"Active Fields"** — count of registered fields with a "+" button
4. **"Crop Recommendation"** — last recommended crop with suitability score
5. **"Moisture Status"** — moisture gauge for each field (color coded)

---

### 4.3 Soil Analysis Page (`/analyze`)

**Step 1 — Upload**
- Large drag-and-drop zone with camera icon
- Mobile: "Take Photo" button
- Shows image preview immediately after selection
- Quality indicator (Good / Poor / Rejected) shown after frontend validation

**Step 2 — Processing**
- Animated spinner with status messages:
  - "Preprocessing image..."
  - "Running soil classifier..."
  - "Estimating moisture..."
  - "Generating recommendations..."

**Step 3 — Results (Same Page, Scrollable)**

```
┌─────────────────────────────────────┐
│  📸 Your Soil Photo                 │
│  [Original Image] [Grad-CAM View]  │  ← toggle button
└─────────────────────────────────────┘

┌──────────────┐  ┌──────────────────┐
│ Soil Type    │  │ Moisture Level   │
│ 🌍 LOAMY    │  │ 💧 28% — WET    │
│ 92% match   │  │ Good for planting│
└──────────────┘  └──────────────────┘

┌─────────────────────────────────────┐
│ Predicted Yield                     │
│ 🌾 4,280 kg/ha                     │
│ Range: 3,890 – 4,670 kg/ha         │
│ ↑ 12% above district average        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Top Crop Recommendations            │
│ 1. Wheat       ████████░░  82%     │
│ 2. Chickpea    ██████░░░░  68%     │
│ 3. Mustard     █████░░░░░  61%     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ What's affecting your yield?        │
│ (SHAP chart — horizontal bar)       │
│ ✅ Soil moisture    +0.34           │
│ ✅ Nitrogen         +0.22           │
│ ⚠️  Temperature     -0.18           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Recommendations                     │
│ 💧 Irrigate: 25mm in next 48 hours │
│ 🌱 Apply NPK 12-32-16 @ 120 kg/ha │
└─────────────────────────────────────┘
```

---

### 4.4 Weather Page (`/weather`)
- Location picker (map or search by district)
- 7-day forecast cards (temperature, rainfall, humidity)
- Agricultural advisories: "Avoid spraying pesticides — high wind expected"
- Line chart: temperature and rainfall over 30 days

---

### 4.5 Field Management (`/fields`)
- List of all fields for the farmer
- Click field → see prediction history for that field
- "Add Field" button → form + map to draw field boundary
- Prediction history: table with date, soil type, moisture, yield estimate

---

### 4.6 Admin Dashboard (`/admin`)
- User count, active users today
- Total predictions run (today / week / month)
- Model accuracy metrics (updated manually or via cron)
- Recent error logs (failed predictions)

---

## 5. Component Library

Using **shadcn/ui** components. Install only what you need:

```bash
npx shadcn-ui@latest add button card badge input label
npx shadcn-ui@latest add table tabs dialog progress
npx shadcn-ui@latest add select toast alert
```

Custom components to build:
- `<SoilTypeBadge type="loamy" />` — colored badge
- `<MoistureGauge value={28} category="WET" />` — arc gauge
- `<GradCamViewer originalUrl="..." heatmapUrl="..." />` — toggle viewer
- `<YieldCard value={4280} range={[3890, 4670]} />` — prediction card
- `<ShapChart factors={[...]} />` — horizontal bar SHAP chart
- `<CropCard name="Wheat" score={0.82} />` — recommendation card

---

## 6. Responsive Breakpoints

```
Mobile:  360px – 639px   → single column, bottom nav
Tablet:  640px – 1023px  → two columns, top nav
Desktop: 1024px+         → three columns, sidebar nav
```

---

## 7. Loading & Error States

- Every data fetch shows a skeleton loader (not a spinner)
- Failed ML inference: show "Analysis failed — please retake photo in better lighting"
- Network error: Toast notification "Connection lost. Retrying..."
- Image quality rejection: Inline message with a photo tip (e.g., "Avoid shadows, take from 30cm above soil")

---

## 8. What NOT to Build in the UI

- Complex onboarding wizards
- In-app tutorials / tooltips carousels
- Dark/light mode toggle (dark mode only for now)
- Profile photo upload
- Social sharing buttons
