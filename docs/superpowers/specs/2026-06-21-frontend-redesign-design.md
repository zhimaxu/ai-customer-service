# Frontend Redesign — Design Spec

> **Date**: 2026-06-21
> **Goal**: Full layout + visual overhaul of the Vue 3 frontend — dark coral-tech theme, unified navigation, animated particles, data visualization upgrade.

---

## 1. Design System

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-deep` | `#0f1117` | Page background, login canvas |
| `--bg-surface` | `#1a1d27` | Cards, panels, sidebar |
| `--bg-elevated` | `#232733` | Hover states, active items |
| `--coral-primary` | `#FF6B35` | Brand accent, user bubbles, CTAs |
| `--coral-light` | `#FF8F66` | Hover glow, highlights |
| `--purple-accent` | `#7C5CFC` | Charts, assistant badge, secondary accent |
| `--text-primary` | `#EAEAEA` | Body text, headings |
| `--text-secondary` | `#9CA3AF` | Meta info, timestamps |
| `--text-muted` | `#6B7280` | Placeholders, empty states |
| `--success` | `#34D399` | Online status, success actions |
| `--warning` | `#FBBF24` | Human-agent status |
| `--danger` | `#EF4444` | Close, delete actions |
| `--border-subtle` | `rgba(255,255,255,0.06)` | Dividers, card borders |

### Typography

- Font family: `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif`
- Heading sizes: 24px (H1), 20px (H2), 16px (H3)
- Body: 14px, line-height 1.6
- Mono (timestamps): 12px, `SF Mono, Consolas, monospace`

### Spacing Scale

`4, 8, 12, 16, 20, 24, 32, 40, 48, 64`

### Border Radius

- Cards: `12px`
- Buttons: `8px`
- Input fields: `8px`
- Avatar circles: `50%`

---

## 2. Global Layout Architecture

### New Structure

```
App.vue (layout wrapper)
├── SidebarNav (collapsible, default 64px / expanded 240px)
├── <router-view />
│   ├── LoginView
│   ├── ChatView
│   ├── AgentView
│   └── DashboardView
```

### SidebarNav (new component)

- **Collapsed state** (~64px): icons only, hover tooltip with label
- **Expanded state** (~240px): icon + text label, active indicator (coral gradient left border + glow)
- Navigation items:
  - 💬 Chat (route `/`)
  - 🎧 Agent (route `/agent`)
  - 📊 Dashboard (route `/dashboard`)
  - ⚙️ Settings (drawer)
- Bottom: user avatar + logout button
- Transition: smooth width change with `transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1)`
- Toggle button: hamburger icon, only visible in expanded state

### CSS Variable Injection

All theme tokens defined in `:root` within `src/style.css` (new file), imported in `main.js`. Components reference tokens via `var(--token)` instead of hardcoded colors.

---

## 3. Page-by-Page Redesign

### 3.1 LoginView

**Current**: Simple centered card on purple-blue gradient background.

**Redesign**:
- Full-screen dark background (`--bg-deep`)
- **Canvas particle network animation**: floating dots connected by lines, coral-colored nodes, subtle opacity pulse
- Centered **frosted-glass card** (`backdrop-filter: blur(20px)`, semi-transparent `--bg-surface`, `border: 1px solid var(--border-subtle)`)
- Card content:
  - Logo: coral gradient text "AI 智能客服" with subtle glow
  - Form fields with dark inputs (`--bg-elevated`), coral focus ring
  - Login button: coral gradient (`linear-gradient(135deg, #FF6B35, #FF8F66)`), hover lift + shadow
  - Tenant ID field: smaller, muted placeholder text
- Loading state: button spinner animation
- Error: coral toast notification sliding in from top-right

**Animation details**:
- Particles: 60-80 dots, random velocity, connection distance < 150px, coral glow pulse every 3s
- Card entrance: fade-in + translateY(20px) on mount
- Input focus: coral bottom-border slide-in animation

### 3.2 ChatView (Customer-Facing)

**Current**: Top bar with logo + settings/logout. SessionList (280px) + ChatWindow side by side.

**Redesign**:
- **Top bar removed** — navigation handled by SidebarNav
- ChatWindow takes full remaining width
- SessionList moves inside SidebarNav as a **slide-out drawer** (triggered by clicking a "sessions" icon in the sidebar, or sidebar expanded showing session list when Chat is active)
- Actually, simpler approach: SessionList becomes a **right panel** (toggleable, 320px width) — shows active sessions for this user
- ChatWindow:
  - Welcome state: large coral gradient heading + subtitle, centered in empty state
  - Message area: dark background (`--bg-deep`), subtle dot grid pattern
  - Input area: frosted glass bar at bottom, coral send button with hover glow
  - Streaming indicator: coral wave animation (3 pulsing dots)

**MessageBubble redesign**:
- User messages: coral gradient background (`#FF6B35 → #FF8F66`), white text, right-aligned, border-top-right-radius 4px
- Assistant messages: `--bg-elevated` background, `--text-primary` text, left-aligned, purple accent icon
- Avatar replaced with circular initials or coral/purple gradient circle
- Timestamp: `--text-muted`, 11px, below bubble
- Streaming cursor: coral blinking caret with glow

**Animation details**:
- New message: spring-in from bottom (scale 0.9 → 1, opacity 0 → 1, 0.3s)
- Session list item hover: background shift + subtle left coral border slide-in
- Input area: focus glow ring on textarea

### 3.3 AgentView (Customer Service Workspace)

**Current**: Green top bar. AgentSidebar (280px) + AgentChat. Tabs for filtering sessions.

**Redesign**:
- **AgentSidebar** becomes the **left portion** of the main area (not inside SidebarNav), split layout:
  - Left panel (320px): session list with dark cards
  - Right panel (flex): chat area
  - Divider: draggable resize handle (coral hover indicator)
- Session list items:
  - Dark card (`--bg-surface`) with rounded corners
  - Status indicator dot (green=active, yellow=human, gray=closed)
  - User ID + last message preview (truncated, 1 line)
  - Agent type badge (AI=coral, Human=purple)
  - Message count + timestamp
  - Unread count: coral pill badge
  - Hover: `--bg-elevated` + coral left border 3px
  - Active: coral left border + subtle glow shadow
- **AgentChat** header:
  - Session info bar: user ID, status tag, agent type tag
  - Action buttons: Takeover (coral), Close (danger)
  - Online status indicator (pulsing green dot)
- Quick replies: coral pill-shaped tags in a scrollable bar
- Input area: dark textarea with coral send button

**Animation details**:
- Session item click: ripple effect from click point
- Takeover button: coral pulse animation on click
- New message arrival (WS): card flash border coral for 0.5s
- Quick reply hover: scale 1.05 + coral glow

### 3.4 DashboardView

**Current**: Purple top bar with nav tabs. Grid of stat cards + ECharts charts.

**Redesign**:
- **Top bar removed** — nav handled by SidebarNav
- Dashboard content fills full area with dark background
- Stat overview cards:
  - 4-column grid, dark glassmorphism cards (`--bg-surface`, `backdrop-filter: blur(10px)`)
  - Each card: large coral number, muted label, small trend arrow (↑↓)
  - Hover: lift + coral glow shadow
  - Icon in top-right corner (coral gradient circle background)
- Charts row:
  - Two equal-width cards side by side
  - Chat Trend: line chart with coral gradient fill under line, purple secondary line
  - Satisfaction: donut chart with coral-to-purple gradient segments
  - Dark theme chart colors: grid lines at 6% white, axes at 30% white
- Efficiency metrics card:
  - Full-width card below charts
  - 4 metric items in a grid
  - Coral numbers, muted labels, subtle divider lines

**Chart color mapping**:
- Total sessions: `#FF6B35` (coral)
- Active: `#34D399` (green)
- Closed: `#FBBF24` (warning)
- Satisfaction 5-star: `#FF6B35`
- Satisfaction 4-star: `#FF8F66`
- Satisfaction 3-star: `#FBBF24`
- Satisfaction 2-star: `#F87171`
- Satisfaction 1-star: `#EF4444`

**Animation details**:
- Number counting animation on load (0 → target over 1s)
- Chart fade-in with stagger (0.2s between cards)
- Period selector (day/week/month): coral underline animation on change
- Card hover: translateY(-2px) + shadow spread

---

## 4. Component Library Upgrades

### New Shared Components

| Component | Purpose |
|-----------|---------|
| `DarkCard` | Reusable dark glassmorphism card with hover glow |
| `CoralButton` | Gradient coral primary button variant |
| `StatusDot` | Pulsing status indicator (online/busy/offline) |
| `ParticleBackground` | Canvas particle network for login page |
| `SkeletonLoader` | Shimmer loading placeholder for async data |

### Updated Components

| Component | Changes |
|-----------|---------|
| `MessageBubble` | Coral gradient bg, spring animation, glow cursor |
| `AgentMessageBubble` | Dark theme, coral user, purple assistant, green agent |
| `SessionList` | Dark cards, status dots, unread badges |
| `TypingIndicator` | Coral wave dots instead of gray |
| `SettingsPanel` | Dark theme drawer, coral sliders |
| `FileUpload` | Coral dashed border, hover glow |

### Transitions

- Page transitions: `<transition name="fade-slide">` — opacity 0→1, translateY 12px→0, duration 0.25s
- Modal/drawer: slide from right, overlay fade
- Toast notifications: slide from top-right, fade out after 3s

---

## 5. Implementation Phases

### Phase 1: Foundation (3-4 hours)
- Create `src/style.css` with all CSS variables
- Create `SidebarNav.vue` component with collapse/expand
- Refactor `App.vue` to use unified layout
- Remove individual top-bars from all views

### Phase 2: Login Page (2-3 hours)
- Implement Canvas particle network
- Frosted glass card design
- Coral gradient form styling
- Animation transitions

### Phase 3: Chat View (3-4 hours)
- Redesign MessageBubble with coral theme
- Update ChatWindow layout
- Spring animations for messages
- Typing indicator wave

### Phase 4: Agent View (3-4 hours)
- Redesign AgentSidebar with dark cards
- AgentChat header + action buttons
- Quick reply pills
- WebSocket notification flash

### Phase 5: Dashboard (2-3 hours)
- Dark glassmorphism stat cards
- ECharts dark theme configuration
- Number counting animation
- Chart color mapping

### Phase 6: Polish (1-2 hours)
- Global hover/focus states
- Responsive breakpoints
- Accessibility contrast check
- Performance optimization (will-change, transform only)

---

## 6. Dependencies

- **No new npm packages needed** — all animations use CSS transitions/transforms, particle canvas is vanilla JS
- Existing dependencies remain: Vue 3, Element Plus, Pinia, ECharts, axios
- Element Plus dark mode: use CSS variable overrides, don't rely on built-in dark theme (too opinionated)

---

## 7. Files to Create/Modify

### New Files
- `frontend/src/style.css` — Global CSS variables, base styles
- `frontend/src/components/SidebarNav.vue` — Collapsible left navigation
- `frontend/src/components/ParticleBackground.vue` — Canvas particle animation
- `frontend/src/components/DarkCard.vue` — Reusable dark card
- `frontend/src/components/StatusDot.vue` — Pulsing status indicator
- `frontend/src/components/SkeletonLoader.vue` — Shimmer loading

### Modified Files
- `frontend/src/App.vue` — Unified layout wrapper
- `frontend/src/main.js` — Import `style.css`
- `frontend/src/router/index.js` — Add page transition
- `frontend/src/views/Login.vue` — Full redesign
- `frontend/src/views/ChatView.vue` — Remove top-bar, adjust layout
- `frontend/src/views/AgentView.vue` — Remove top-bar, adjust layout
- `frontend/src/views/DashboardView.vue` — Remove top-bar, dark theme
- `frontend/src/components/MessageBubble.vue` — Coral gradient
- `frontend/src/components/AgentMessageBubble.vue` — Dark theme
- `frontend/src/components/ChatWindow.vue` — Dark input area
- `frontend/src/components/SessionList.vue` — Dark cards
- `frontend/src/components/AgentSidebar.vue` — Dark cards, status dots
- `frontend/src/components/AgentChat.vue` — Coral actions
- `frontend/src/components/TypingIndicator.vue` — Coral wave
- `frontend/src/components/SettingsPanel.vue` — Dark theme
- `frontend/src/components/FileUpload.vue` — Coral styling
- `frontend/src/stores/session.js` — Minor: no changes needed
- `frontend/src/stores/agent.js` — Minor: no changes needed
- `frontend/src/api/request.js` — Minor: no changes needed
