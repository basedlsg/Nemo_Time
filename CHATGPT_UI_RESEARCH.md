# ChatGPT UI/UX Research Report
## Comprehensive Guide to Cloning the ChatGPT Interface

**Report Date:** 2025-11-20
**Purpose:** Research and document the exact ChatGPT user interface for cloning it for the Nemo energy compliance platform
**Target Accuracy:** 90%+ UI/UX replication

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Top Open Source Implementations](#top-open-source-implementations)
3. [Recommended Tech Stack](#recommended-tech-stack)
4. [Design System Overview](#design-system-overview)
5. [Component-by-Component Breakdown](#component-by-component-breakdown)
6. [Layout & Spacing Guidelines](#layout--spacing-guidelines)
7. [Interaction Patterns](#interaction-patterns)
8. [Color Palette & Theming](#color-palette--theming)
9. [Responsive Design](#responsive-design)
10. [Code Examples & Implementation](#code-examples--implementation)
11. [Figma & Design Resources](#figma--design-resources)
12. [References & Links](#references--links)

---

## Executive Summary

ChatGPT's interface is characterized by:
- **Clean, minimal design** with focus on conversation
- **Full-width message layout** (not bubble-based)
- **Collapsible sidebar** for conversation history
- **Auto-resizing textarea** with streaming responses
- **Markdown rendering** with syntax-highlighted code blocks
- **Dark/Light mode support** with system font stack
- **Responsive design** optimized for mobile, tablet, and desktop

**Primary Font:** Inter (web), OpenAI Sans (brand, 2025), with system font fallbacks
**Framework Recommendation:** React + TypeScript + Tailwind CSS + shadcn/ui
**Key Libraries:** react-markdown, highlight.js, framer-motion (optional for animations)

---

## Top Open Source Implementations

### 1. LibreChat ⭐⭐⭐⭐⭐ (Most Feature-Complete)

**GitHub:** https://github.com/danny-avila/LibreChat

**Tech Stack:**
- TypeScript (65.6%) + JavaScript (32.9%)
- React frontend
- Node.js backend
- Docker deployment
- Bun package manager support

**Key Features:**
- UI & Experience inspired by ChatGPT with enhanced design
- Multi-model support (OpenAI, Claude, Gemini, etc.)
- Code Interpreter API with sandboxed execution
- No-code custom assistants
- Conversation branching and message editing
- Dynamic Reasoning UI for chain-of-thought models
- Code Artifacts (React/HTML/Mermaid diagrams)
- 24+ language support
- Speech-to-text and text-to-speech

**Why Use It:**
- Most production-ready
- Best UI/UX implementation
- Active development and community
- Comprehensive feature set

---

### 2. BetterChatGPT ⭐⭐⭐⭐ (Best for Simplicity)

**GitHub:** https://github.com/ztjhz/BetterChatGPT
**Live Demo:** https://bettergpt.chat/

**Tech Stack:**
- TypeScript (93.4%)
- React + Vite
- Tailwind CSS
- Electron (cross-platform desktop)
- PostCSS

**Key Features:**
- Proxy to bypass regional restrictions
- Prompt library
- Chat folders with colors
- Token counting with pricing
- ShareGPT integration
- Custom model parameters
- Message editing (edit, reorder, insert anywhere)
- Export (markdown, image, JSON)
- Google Drive sync
- Azure OpenAI support
- Multilingual (i18n)
- Chat title generator
- Auto-save to local storage
- Unlimited local storage (desktop app)

**Why Use It:**
- Clean, simple codebase
- Great for learning
- Cross-platform (web + desktop)
- Active community

---

### 3. Chatbot UI ⭐⭐⭐⭐ (Modern Stack)

**GitHub:** https://github.com/mckaywrigley/chatbot-ui

**Tech Stack:**
- Next.js (React)
- TypeScript (95.7%)
- Supabase (PostgreSQL)
- Tailwind CSS
- shadcn/ui components
- Docker support
- Ollama integration (local models)

**Key Features:**
- AI chat for any model
- Multi-modal support (vision)
- File storage and management
- Improved mobile layouts
- Backend GUI interface
- Support for OpenAI, Azure, local models

**Why Use It:**
- Modern Next.js architecture
- shadcn/ui component library
- Great mobile support
- Database-backed (Supabase)

---

### 4. Specialized Component Libraries

#### **LangUI**
**GitHub:** https://github.com/LangbaseInc/langui

- 60+ free Tailwind components for AI/GPT projects
- Specialized for LLM applications
- Production-ready components

#### **chat-components**
**GitHub:** https://github.com/miskibin/chat-components

- Customizable, accessible ChatGPT-like UI components
- Built with shadcn/ui design system
- React-focused

#### **react-chat-stream**
**GitHub:** https://github.com/XD2Sketch/react-chat-stream

- React Hook for ChatGPT-like word-by-word streaming
- Lightweight and focused

---

## Recommended Tech Stack

### Core Technologies

```json
{
  "framework": "React 18+",
  "language": "TypeScript",
  "bundler": "Vite or Next.js",
  "styling": "Tailwind CSS 3.x",
  "components": "shadcn/ui",
  "routing": "React Router or Next.js App Router"
}
```

### Essential Libraries

```json
{
  "markdown": "react-markdown",
  "syntaxHighlighting": "highlight.js or prism-react-renderer",
  "streaming": "@magicul/react-chat-stream or custom hook",
  "stateManagement": "React Context or Zustand",
  "apiClient": "OpenAI SDK or custom fetch",
  "animations": "framer-motion (optional)",
  "icons": "lucide-react or heroicons"
}
```

### Development Tools

```json
{
  "linting": "ESLint",
  "formatting": "Prettier",
  "testing": "Jest + React Testing Library",
  "typeChecking": "TypeScript strict mode",
  "gitHooks": "Husky"
}
```

---

## Design System Overview

### Typography

**Primary Font:** Inter
- Web interface uses Inter font family
- Fallback: System font stack (Segoe UI, San Francisco, Roboto)
- Brand font (2025): OpenAI Sans (custom typeface)

**Font Sizes:**
```css
/* Common ChatGPT font sizes */
--font-xs: 0.75rem;    /* 12px */
--font-sm: 0.875rem;   /* 14px */
--font-base: 1rem;     /* 16px - main text */
--font-lg: 1.125rem;   /* 18px */
--font-xl: 1.25rem;    /* 20px */
--font-2xl: 1.5rem;    /* 24px - headings */
```

**Font Weights:**
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

**Line Heights:**
```css
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

---

### Color Palette

**Official Brand Colors:**
```css
/* ChatGPT Brand */
--brand-green: #00A67E;
--brand-white: #FFFFFF;
--brand-purple: #ab68ff;
--brand-teal: #74aa9c;
```

**Light Mode (Approximated):**
```css
/* Background */
--bg-primary: #FFFFFF;
--bg-secondary: #F7F7F8;
--bg-tertiary: #ECECF1;

/* Text */
--text-primary: #0D0D0D;
--text-secondary: #565869;
--text-tertiary: #8E8EA0;

/* Borders */
--border-light: #E5E5E5;
--border-medium: #D1D1D6;

/* Message backgrounds */
--message-user-bg: #F7F7F8;
--message-assistant-bg: #FFFFFF;

/* Buttons */
--button-primary: #0D0D0D;
--button-secondary: #F7F7F8;
--button-hover: #ECECF1;
```

**Dark Mode (Approximated):**
```css
/* Background */
--bg-primary: #0D0D0D;
--bg-secondary: #1A1A1A;
--bg-tertiary: #2A2A2A;

/* Text */
--text-primary: #ECECEC;
--text-secondary: #B4B4B4;
--text-tertiary: #8E8EA0;

/* Borders */
--border-light: #2A2A2A;
--border-medium: #3C3C3C;

/* Message backgrounds */
--message-user-bg: #2A2A2A;
--message-assistant-bg: #0D0D0D;

/* Buttons */
--button-primary: #FFFFFF;
--button-secondary: #2A2A2A;
--button-hover: #3C3C3C;
```

**Note:** These colors are approximated from community observations. Use browser DevTools to inspect the actual ChatGPT interface for precise values.

---

### Spacing System

ChatGPT follows a consistent spacing scale:

```css
/* Tailwind-compatible spacing */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

---

## Component-by-Component Breakdown

### 1. Overall Layout Structure

```
┌─────────────────────────────────────────────────────┐
│  [Sidebar]  │  [Main Chat Area]                      │
│  (260px)    │  [Header Bar]                          │
│             │  ┌──────────────────────────────────┐  │
│  [History]  │  │  [Messages Container]            │  │
│             │  │  - User Message                  │  │
│  [New Chat] │  │  - Assistant Message             │  │
│             │  │  - User Message                  │  │
│  [Settings] │  │  - Assistant Message (streaming) │  │
│             │  └──────────────────────────────────┘  │
│             │  [Input Area]                          │
└─────────────────────────────────────────────────────┘
```

**Layout Specifications:**
- Sidebar width: `260px` (expanded), `50px` (collapsed)
- Sidebar height: `100vh` (full viewport)
- Sidebar position: `fixed` (left side)
- Main content: `margin-left: 260px` or `50px`
- Max content width: `768px - 900px` (centered)

---

### 2. Sidebar Navigation

**Structure:**
```
┌─────────────────────┐
│ [OpenAI Logo]       │
│ [New Chat Button]   │
│ ─────────────────── │
│ [Today]             │
│  - Chat 1           │
│  - Chat 2           │
│ [Yesterday]         │
│  - Chat 3           │
│ [Previous 7 Days]   │
│  - Chat 4           │
│ ─────────────────── │
│ [Settings]          │
│ [User Profile]      │
└─────────────────────┘
```

**Specifications:**
- Background: Dark/light based on theme
- Width: 260px (expanded)
- Padding: 12px - 16px
- New Chat button: Full width, rounded corners, accent color
- Chat items: Truncate with ellipsis, hover state
- Grouped by date (Today, Yesterday, Previous 7 Days, etc.)
- Scroll: Overflow-y auto

**Key Features:**
- Collapsible (hamburger icon)
- Conversation folders/organization
- Search conversations
- Delete/rename conversations (on hover)
- Smooth transitions (200-300ms)

**CSS Example:**
```css
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 260px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease;
}

.sidebar.collapsed {
  width: 50px;
}

.chat-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: background 0.15s ease;
}

.chat-item:hover {
  background: var(--bg-tertiary);
}
```

---

### 3. Top Navigation Bar / Header

**Structure:**
```
┌──────────────────────────────────────────────────┐
│ [☰] [Model Selector ▼] [Share] [User Avatar ▼]  │
└──────────────────────────────────────────────────┘
```

**Specifications:**
- Height: `48px - 56px`
- Position: Sticky or fixed at top
- Padding: `12px 16px`
- Background: Transparent or solid (depending on scroll)
- Border-bottom: 1px on scroll

**Components:**
1. **Hamburger Menu** (mobile/collapsed sidebar toggle)
2. **Model Selector Dropdown** (GPT-4, GPT-3.5, etc.)
3. **Action Buttons** (Share, etc.)
4. **User Profile Menu** (Settings, Logout, etc.)

---

### 4. Messages Container

**Message Layout:**

ChatGPT uses **full-width messages**, NOT speech bubbles.

```
┌─────────────────────────────────────────────────┐
│ [User Avatar] User Message Text                 │
│               Continues full width...            │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ [AI Avatar] Assistant response here...          │
│             **Bold text**, *italic*, code        │
│             - Lists                              │
│             [Copy] [Regenerate] [Good/Bad]       │
└─────────────────────────────────────────────────┘
```

**User Message Specifications:**
- Background: Light gray (light mode) / Dark gray (dark mode)
- Padding: `16px 24px`
- Avatar: Left-aligned, 28px - 32px circle
- Text: Left-aligned, full width
- Font: 16px, regular weight
- Line-height: 1.5

**Assistant Message Specifications:**
- Background: White (light mode) / Darker shade (dark mode)
- Padding: `16px 24px`
- Avatar: ChatGPT logo/icon, 28px - 32px
- Text: Left-aligned, markdown-rendered
- Code blocks: Syntax highlighted
- Action buttons: Bottom of message (Copy, Regenerate, etc.)

**Spacing:**
- Gap between messages: `16px - 24px`
- Max width: `768px - 900px` (centered)

**CSS Example:**
```css
.message-container {
  max-width: 768px;
  margin: 0 auto;
  padding: 16px 24px;
}

.message-user {
  background: var(--message-user-bg);
  padding: 16px 24px;
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.message-assistant {
  background: var(--message-assistant-bg);
  padding: 16px 24px;
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  line-height: 1.5;
}
```

---

### 5. Input Box / Textarea

**Structure:**
```
┌─────────────────────────────────────────────────┐
│ Send a message...                               │
│ [Attach] [Voice]                       [Send ➤] │
└─────────────────────────────────────────────────┘
```

**Specifications:**
- Position: Fixed at bottom or in flow
- Width: Constrained (max-width: 768px - 900px)
- Min-height: `48px - 56px`
- Max-height: `200px` (with auto-resize)
- Border-radius: `12px - 16px`
- Border: 1px solid (thicker on focus)
- Padding: `12px 16px`
- Box-shadow on focus

**Features:**
- **Auto-resize** as user types (grows vertically)
- Multiline support
- Shift+Enter for new line, Enter to send
- Attachment button (left)
- Voice input button (optional)
- Send button (right, disabled when empty)
- Character/token counter (optional)

**Auto-resize Implementation:**

```jsx
// React implementation
const handleInput = (e) => {
  const textarea = e.target;
  textarea.style.height = '0px'; // Reset
  textarea.style.height = `${textarea.scrollHeight}px`; // Set to content height
};

// Usage
<textarea
  ref={textareaRef}
  onInput={handleInput}
  placeholder="Send a message..."
  rows="1"
  style={{ maxHeight: '200px', resize: 'none' }}
/>
```

**CSS Example:**
```css
.input-container {
  position: sticky;
  bottom: 0;
  padding: 16px;
  background: var(--bg-primary);
  border-top: 1px solid var(--border-light);
}

.input-wrapper {
  max-width: 768px;
  margin: 0 auto;
  position: relative;
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
  border-radius: 16px;
  padding: 12px 16px;
  display: flex;
  align-items: flex-end;
  gap: 8px;
  transition: border-color 0.15s ease;
}

.input-wrapper:focus-within {
  border-color: var(--brand-green);
  box-shadow: 0 0 0 3px rgba(0, 166, 126, 0.1);
}

.input-textarea {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  line-height: 1.5;
  resize: none;
  max-height: 200px;
  overflow-y: auto;
}

.send-button {
  background: var(--button-primary);
  color: var(--text-primary);
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.send-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
```

---

### 6. Code Block Rendering

**Structure:**
```
┌─────────────────────────────────────────────────┐
│ javascript                            [Copy]    │
├─────────────────────────────────────────────────┤
│ const greeting = "Hello, world!";               │
│ console.log(greeting);                          │
└─────────────────────────────────────────────────┘
```

**Specifications:**
- Background: Dark (even in light mode for code)
- Border-radius: `8px`
- Padding: `16px`
- Font: Monospace (Monaco, Consolas, Courier New)
- Font-size: `14px`
- Header bar: Language + Copy button
- Syntax highlighting: highlight.js or Prism.js
- Line numbers: Optional
- Word wrap: Optional toggle

**Implementation:**

```jsx
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const MarkdownRenderer = ({ content }) => {
  return (
    <ReactMarkdown
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <div className="code-block">
              <div className="code-header">
                <span>{match[1]}</span>
                <button onClick={() => copyToClipboard(children)}>
                  Copy
                </button>
              </div>
              <SyntaxHighlighter
                style={oneDark}
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            </div>
          ) : (
            <code className="inline-code" {...props}>
              {children}
            </code>
          );
        }
      }}
    >
      {content}
    </ReactMarkdown>
  );
};
```

**CSS Example:**
```css
.code-block {
  margin: 16px 0;
  border-radius: 8px;
  overflow: hidden;
  background: #1e1e1e;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #2d2d2d;
  color: #abb2bf;
  font-size: 14px;
}

.code-header button {
  background: transparent;
  border: 1px solid #4d4d4d;
  color: #abb2bf;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.code-header button:hover {
  background: #3d3d3d;
  border-color: #6d6d6d;
}

.inline-code {
  background: rgba(135, 131, 120, 0.15);
  color: #eb5757;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.9em;
}
```

---

### 7. Message Action Buttons

**Buttons displayed at the end of assistant messages:**

1. **Copy Button** - Copies message to clipboard
2. **Regenerate Response** - Sends same prompt again
3. **Thumbs Up/Down** - Feedback buttons
4. **Share** - Share conversation (optional)

**Specifications:**
- Size: Small (24px - 28px)
- Style: Icon-only, minimal
- Color: Subtle gray, darker on hover
- Position: Below message content
- Spacing: 8px gap between buttons
- Hover state: Background fill + icon color change

**Implementation:**

```jsx
const MessageActions = ({ message, onCopy, onRegenerate }) => {
  return (
    <div className="message-actions">
      <button
        onClick={() => onCopy(message.content)}
        className="action-button"
        aria-label="Copy message"
      >
        <CopyIcon />
      </button>
      <button
        onClick={() => onRegenerate()}
        className="action-button"
        aria-label="Regenerate response"
      >
        <RefreshIcon />
      </button>
      <button className="action-button" aria-label="Good response">
        <ThumbsUpIcon />
      </button>
      <button className="action-button" aria-label="Bad response">
        <ThumbsDownIcon />
      </button>
    </div>
  );
};
```

**CSS:**
```css
.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.action-button {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-tertiary);
  padding: 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-button:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}
```

---

### 8. Settings/Profile Menu

**Dropdown menu structure:**
```
┌─────────────────────────┐
│ [Avatar] User Name      │
│ user@email.com          │
├─────────────────────────┤
│ ⚙️  Settings             │
│ 💬 My Plan               │
│ 🔄 Custom Instructions   │
├─────────────────────────┤
│ 🌙 Dark Mode   [Toggle] │
├─────────────────────────┤
│ 🚪 Log out               │
└─────────────────────────┘
```

**Specifications:**
- Width: `260px - 280px`
- Border-radius: `8px`
- Box-shadow: Elevated (0 4px 12px rgba(0,0,0,0.15))
- Background: var(--bg-primary)
- Border: 1px solid var(--border-light)
- Padding: 8px
- Animation: Fade in + slide down (150ms)

---

### 9. Loading States

#### **Typing Indicator (Three Dots)**

Visual representation while AI is "thinking":

```
● ● ●  (animated bouncing)
```

**Implementation:**

```jsx
const TypingIndicator = () => {
  return (
    <div className="typing-indicator">
      <span className="dot"></span>
      <span className="dot"></span>
      <span className="dot"></span>
    </div>
  );
};
```

**CSS Animation:**
```css
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 16px;
}

.dot {
  width: 8px;
  height: 8px;
  background: var(--text-tertiary);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: translateY(0);
    opacity: 0.6;
  }
  40% {
    transform: translateY(-10px);
    opacity: 1;
  }
}
```

#### **Streaming Text Animation**

Text appears word-by-word or character-by-character:

**Implementation:**

```jsx
const StreamingMessage = ({ content, isStreaming }) => {
  const [displayedContent, setDisplayedContent] = useState('');
  const contentRef = useRef('');

  useEffect(() => {
    if (!isStreaming) {
      setDisplayedContent(content);
      return;
    }

    // Buffer approach for performance
    contentRef.current = content;

    const interval = setInterval(() => {
      setDisplayedContent(prev => {
        if (prev.length < contentRef.current.length) {
          return contentRef.current.slice(0, prev.length + 3); // Add 3 chars at a time
        }
        return prev;
      });
    }, 30); // Update every 30ms

    return () => clearInterval(interval);
  }, [content, isStreaming]);

  return (
    <div className="message-content">
      <ReactMarkdown>{displayedContent}</ReactMarkdown>
      {isStreaming && <span className="cursor">▊</span>}
    </div>
  );
};
```

**Cursor Animation:**
```css
.cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: var(--text-primary);
  margin-left: 2px;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
```

---

### 10. Error States

**Error Message Display:**

```
┌─────────────────────────────────────────────────┐
│ ⚠️ Something went wrong                          │
│                                                  │
│ [Error message details here]                     │
│                                                  │
│ [Retry] [Cancel]                                │
└─────────────────────────────────────────────────┘
```

**Common Error Types:**
1. **Rate Limit Error (429):** "Too many requests. Please wait and try again."
2. **Network Error:** "Network connection lost. Please check your connection."
3. **Server Error (500):** "ChatGPT is currently experiencing issues. Please try again later."
4. **Authentication Error:** "Your session has expired. Please log in again."

**Implementation:**

```jsx
const ErrorMessage = ({ error, onRetry, onDismiss }) => {
  const errorMessages = {
    429: "You're sending too many requests. Please wait a moment.",
    500: "ChatGPT is experiencing issues. Please try again later.",
    401: "Your session has expired. Please log in again.",
    network: "Network connection lost. Please check your connection."
  };

  return (
    <div className="error-message">
      <div className="error-icon">⚠️</div>
      <div className="error-content">
        <h4 className="error-title">Something went wrong</h4>
        <p className="error-description">
          {errorMessages[error.code] || error.message}
        </p>
      </div>
      <div className="error-actions">
        {onRetry && <button onClick={onRetry}>Retry</button>}
        <button onClick={onDismiss}>Dismiss</button>
      </div>
    </div>
  );
};
```

**CSS:**
```css
.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.error-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.error-content {
  flex: 1;
}

.error-title {
  font-weight: 600;
  color: #991b1b;
  margin-bottom: 4px;
}

.error-description {
  color: #7f1d1d;
  font-size: 14px;
}

.error-actions {
  display: flex;
  gap: 8px;
}
```

---

### 11. Empty State (New Chat)

**Initial state when no messages:**

```
┌─────────────────────────────────────────────────┐
│                                                  │
│               [ChatGPT Logo]                     │
│                                                  │
│           How can I help you today?              │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐             │
│  │ 💡 Suggest     │  │ 📝 Write an   │             │
│  │ fun activities │  │ email        │             │
│  └──────────────┘  └──────────────┘             │
│  ┌──────────────┐  ┌──────────────┐             │
│  │ 🧮 Help with   │  │ 🎨 Create a   │             │
│  │ math          │  │ design       │             │
│  └──────────────┘  └──────────────┘             │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Specifications:**
- Centered vertically and horizontally
- Large logo/icon (48px - 64px)
- Greeting text (24px - 28px, semi-bold)
- Suggestion cards (4-6 examples)
- Card specs: Padding 16px, border 1px, rounded 12px, hover effect

**Implementation:**

```jsx
const EmptyState = ({ onSelectPrompt }) => {
  const suggestions = [
    { icon: "💡", text: "Suggest fun activities", prompt: "Suggest some fun activities for..." },
    { icon: "📝", text: "Write an email", prompt: "Write a professional email about..." },
    { icon: "🧮", text: "Help with math", prompt: "Help me solve this math problem..." },
    { icon: "🎨", text: "Create a design", prompt: "Create a design concept for..." }
  ];

  return (
    <div className="empty-state">
      <div className="empty-state-logo">
        <ChatGPTLogo size={64} />
      </div>
      <h2 className="empty-state-title">How can I help you today?</h2>
      <div className="suggestion-grid">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            className="suggestion-card"
            onClick={() => onSelectPrompt(suggestion.prompt)}
          >
            <span className="suggestion-icon">{suggestion.icon}</span>
            <span className="suggestion-text">{suggestion.text}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
```

**CSS:**
```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 32px;
}

.empty-state-logo {
  margin-bottom: 24px;
}

.empty-state-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 32px;
  color: var(--text-primary);
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  max-width: 768px;
  width: 100%;
}

.suggestion-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 16px;
  text-align: left;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  gap: 12px;
  align-items: center;
}

.suggestion-card:hover {
  background: var(--bg-tertiary);
  border-color: var(--border-medium);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.suggestion-icon {
  font-size: 24px;
}

.suggestion-text {
  font-size: 14px;
  color: var(--text-primary);
}
```

---

### 12. Stop Generating Button

**Appears during streaming response:**

```
┌─────────────────────────────────────────────────┐
│ Assistant is typing...                          │
│ [⏹️ Stop Generating]                             │
└─────────────────────────────────────────────────┘
```

**Implementation:**

```jsx
const MessageInput = ({ isGenerating, onStopGenerating, onSendMessage }) => {
  return (
    <div className="input-container">
      {isGenerating ? (
        <button
          className="stop-button"
          onClick={onStopGenerating}
        >
          <StopIcon />
          Stop Generating
        </button>
      ) : (
        <button
          className="send-button"
          onClick={onSendMessage}
        >
          <SendIcon />
        </button>
      )}
    </div>
  );
};

// Server-side implementation
const handleStopGenerating = () => {
  // Abort the fetch request
  abortController.abort();

  // Or for streaming APIs
  if (connection_aborted()) {
    break; // Exit streaming loop
  }
};
```

**CSS:**
```css
.stop-button {
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: background 0.15s ease;
}

.stop-button:hover {
  background: #b91c1c;
}
```

---

## Layout & Spacing Guidelines

### Container Widths

```css
/* Main content area */
.chat-container {
  max-width: 768px; /* Primary constraint */
  margin: 0 auto;
  padding: 0 16px;
}

/* Wide layout (optional) */
.chat-container-wide {
  max-width: 900px;
}

/* Sidebar */
.sidebar {
  width: 260px;
}

.sidebar.collapsed {
  width: 50px;
}
```

### Message Spacing

```css
/* Vertical spacing between messages */
.message + .message {
  margin-top: 16px; /* Can be 16px - 24px */
}

/* Internal message padding */
.message {
  padding: 16px 24px;
}

/* Avatar spacing */
.message-avatar {
  margin-right: 16px;
}
```

### Responsive Padding

```css
/* Mobile */
@media (max-width: 640px) {
  .message {
    padding: 12px 16px;
  }

  .chat-container {
    padding: 0 12px;
  }
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
  .message {
    padding: 16px 20px;
  }
}

/* Desktop */
@media (min-width: 1025px) {
  .message {
    padding: 16px 24px;
  }
}
```

### Border Radius

```css
/* Consistent border radius values */
--radius-sm: 4px;   /* Small elements (badges, tags) */
--radius-md: 8px;   /* Buttons, cards */
--radius-lg: 12px;  /* Input boxes, modals */
--radius-xl: 16px;  /* Large containers */
--radius-full: 9999px; /* Avatars, pills */
```

---

## Interaction Patterns

### 1. Hover Effects

**Standard Hover Transition:**
```css
.interactive-element {
  transition: all 0.15s ease;
}

.interactive-element:hover {
  background: var(--bg-tertiary);
  transform: translateY(-1px);
}
```

**Button Hover:**
```css
.button {
  transition: all 0.15s ease;
}

.button:hover {
  background: var(--button-hover);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

**Chat Item Hover:**
```css
.chat-item:hover {
  background: var(--bg-tertiary);
}

.chat-item:hover .chat-actions {
  opacity: 1; /* Show delete/edit buttons */
}
```

---

### 2. Focus States

**Input Focus:**
```css
.input:focus {
  outline: none;
  border-color: var(--brand-green);
  box-shadow: 0 0 0 3px rgba(0, 166, 126, 0.1);
}
```

**Button Focus:**
```css
.button:focus-visible {
  outline: 2px solid var(--brand-green);
  outline-offset: 2px;
}
```

---

### 3. Active States

**Button Click:**
```css
.button:active {
  transform: scale(0.98);
}
```

---

### 4. Disabled States

```css
.button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}
```

---

### 5. Animations & Transitions

**Fade In:**
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message {
  animation: fadeIn 0.2s ease;
}
```

**Slide In:**
```css
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.sidebar {
  animation: slideIn 0.2s ease;
}
```

**Smooth Scroll:**
```css
.messages-container {
  scroll-behavior: smooth;
}

/* Auto-scroll to bottom */
.messages-container {
  overflow-y: auto;
}

// JavaScript
messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
```

---

### 6. Message Streaming Flow

**User Journey:**
1. User types message → Input grows with content
2. User presses Enter → Message appears instantly
3. Loading indicator shows (three dots)
4. Assistant message appears → Streams word-by-word
5. "Stop Generating" button available during streaming
6. Action buttons appear when complete (Copy, Regenerate, etc.)

---

## Color Palette & Theming

### Theme Implementation

**Using CSS Variables:**

```css
/* Root - Light Theme (default) */
:root {
  --bg-primary: #FFFFFF;
  --bg-secondary: #F7F7F8;
  --bg-tertiary: #ECECF1;

  --text-primary: #0D0D0D;
  --text-secondary: #565869;
  --text-tertiary: #8E8EA0;

  --border-light: #E5E5E5;
  --border-medium: #D1D1D6;

  --brand-green: #00A67E;
  --brand-purple: #ab68ff;
}

/* Dark Theme */
[data-theme="dark"] {
  --bg-primary: #0D0D0D;
  --bg-secondary: #1A1A1A;
  --bg-tertiary: #2A2A2A;

  --text-primary: #ECECEC;
  --text-secondary: #B4B4B4;
  --text-tertiary: #8E8EA0;

  --border-light: #2A2A2A;
  --border-medium: #3C3C3C;
}
```

**Theme Toggle Implementation:**

```jsx
const ThemeToggle = () => {
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <button onClick={toggleTheme}>
      {theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}
    </button>
  );
};
```

**System Preference Detection:**

```jsx
useEffect(() => {
  const savedTheme = localStorage.getItem('theme');

  if (savedTheme) {
    setTheme(savedTheme);
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setTheme(prefersDark ? 'dark' : 'light');
  }
}, []);
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile First Approach */

/* Mobile (default) */
@media (max-width: 640px) {
  .sidebar {
    position: fixed;
    transform: translateX(-100%);
    z-index: 50;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .chat-container {
    padding: 0 12px;
  }

  .message {
    padding: 12px 16px;
  }
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
  .sidebar {
    width: 240px;
  }

  .chat-container {
    margin-left: 240px;
  }
}

/* Desktop */
@media (min-width: 1025px) {
  .sidebar {
    width: 260px;
  }

  .chat-container {
    margin-left: 260px;
  }
}
```

### Mobile Optimizations

**Mobile Sidebar (Overlay):**
```jsx
const MobileSidebar = ({ isOpen, onClose }) => {
  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="sidebar-overlay"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        {/* Sidebar content */}
      </aside>
    </>
  );
};
```

**CSS:**
```css
/* Mobile sidebar overlay */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 40;
  animation: fadeIn 0.2s ease;
}

@media (max-width: 640px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    z-index: 50;
  }

  .sidebar.open {
    transform: translateX(0);
  }
}
```

**Touch Optimizations:**
```css
/* Larger touch targets on mobile */
@media (max-width: 640px) {
  .button {
    min-height: 44px; /* iOS recommended touch target */
    padding: 12px 16px;
  }

  .chat-item {
    min-height: 48px;
    padding: 12px;
  }
}
```

---

## Code Examples & Implementation

### Complete React + TypeScript Component Structure

```
src/
├── components/
│   ├── Chat/
│   │   ├── ChatContainer.tsx
│   │   ├── MessageList.tsx
│   │   ├── Message.tsx
│   │   ├── UserMessage.tsx
│   │   ├── AssistantMessage.tsx
│   │   ├── MessageInput.tsx
│   │   ├── TypingIndicator.tsx
│   │   └── EmptyState.tsx
│   ├── Sidebar/
│   │   ├── Sidebar.tsx
│   │   ├── ConversationList.tsx
│   │   ├── ConversationItem.tsx
│   │   └── NewChatButton.tsx
│   ├── Markdown/
│   │   ├── MarkdownRenderer.tsx
│   │   └── CodeBlock.tsx
│   ├── UI/
│   │   ├── Button.tsx
│   │   ├── Avatar.tsx
│   │   ├── Dropdown.tsx
│   │   └── ErrorMessage.tsx
│   └── Layout/
│       ├── AppLayout.tsx
│       ├── Header.tsx
│       └── ThemeToggle.tsx
├── hooks/
│   ├── useChat.ts
│   ├── useStreaming.ts
│   ├── useAutoResize.ts
│   └── useTheme.ts
├── lib/
│   ├── api.ts
│   ├── markdown.ts
│   └── utils.ts
├── types/
│   └── chat.ts
└── styles/
    ├── globals.css
    └── themes.css
```

---

### Example: Main Chat Container

```tsx
// src/components/Chat/ChatContainer.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Message } from '@/types/chat';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import EmptyState from './EmptyState';

interface ChatContainerProps {
  conversationId?: string;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  conversationId
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    // Start streaming
    setIsStreaming(true);

    try {
      // Call API with streaming
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          stream: true
        })
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value);
        assistantMessage += chunk;

        // Update streaming message
        setMessages(prev => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];

          if (lastMessage?.role === 'assistant') {
            lastMessage.content = assistantMessage;
          } else {
            newMessages.push({
              id: Date.now().toString(),
              role: 'assistant',
              content: assistantMessage,
              timestamp: new Date()
            });
          }

          return newMessages;
        });
      }
    } catch (error) {
      console.error('Error:', error);
      // Handle error
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="chat-container">
      {messages.length === 0 ? (
        <EmptyState onSelectPrompt={handleSendMessage} />
      ) : (
        <MessageList
          messages={messages}
          isStreaming={isStreaming}
        />
      )}

      <div ref={messagesEndRef} />

      <MessageInput
        onSendMessage={handleSendMessage}
        isStreaming={isStreaming}
        disabled={isStreaming}
      />
    </div>
  );
};
```

---

### Example: Message Component

```tsx
// src/components/Chat/Message.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Message as MessageType } from '@/types/chat';
import CodeBlock from '../Markdown/CodeBlock';
import MessageActions from './MessageActions';

interface MessageProps {
  message: MessageType;
  isStreaming?: boolean;
}

export const Message: React.FC<MessageProps> = ({
  message,
  isStreaming = false
}) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message message-${message.role}`}>
      <div className="message-avatar">
        {isUser ? (
          <UserAvatar />
        ) : (
          <AssistantAvatar />
        )}
      </div>

      <div className="message-content">
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <>
            <ReactMarkdown
              components={{
                code: CodeBlock
              }}
            >
              {message.content}
            </ReactMarkdown>

            {isStreaming && <span className="cursor">▊</span>}

            {!isStreaming && (
              <MessageActions message={message} />
            )}
          </>
        )}
      </div>
    </div>
  );
};
```

---

### Example: Auto-Resize Textarea Hook

```tsx
// src/hooks/useAutoResize.ts
import { useEffect, RefObject } from 'react';

export const useAutoResize = (
  textareaRef: RefObject<HTMLTextAreaElement>,
  value: string,
  maxHeight: number = 200
) => {
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to auto to get correct scrollHeight
    textarea.style.height = '0px';

    // Set height based on content
    const scrollHeight = textarea.scrollHeight;
    textarea.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
  }, [value, textareaRef, maxHeight]);
};

// Usage:
const MessageInput = () => {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useAutoResize(textareaRef, value, 200);

  return (
    <textarea
      ref={textareaRef}
      value={value}
      onChange={(e) => setValue(e.target.value)}
      placeholder="Send a message..."
      rows={1}
    />
  );
};
```

---

### Example: Streaming Hook

```tsx
// src/hooks/useStreaming.ts
import { useState, useRef, useCallback } from 'react';

interface UseStreamingOptions {
  onComplete?: (content: string) => void;
  onError?: (error: Error) => void;
}

export const useStreaming = (options: UseStreamingOptions = {}) => {
  const [content, setContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const startStreaming = useCallback(async (endpoint: string, body: any) => {
    setIsStreaming(true);
    setContent('');

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: abortControllerRef.current.signal
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value);
        fullContent += chunk;
        setContent(fullContent);
      }

      options.onComplete?.(fullContent);
    } catch (error) {
      if (error.name !== 'AbortError') {
        options.onError?.(error as Error);
      }
    } finally {
      setIsStreaming(false);
    }
  }, [options]);

  const stopStreaming = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsStreaming(false);
  }, []);

  return {
    content,
    isStreaming,
    startStreaming,
    stopStreaming
  };
};
```

---

### Example: Complete shadcn/ui Setup

**1. Install shadcn/ui:**
```bash
npx shadcn-ui@latest init
```

**2. Add components:**
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add textarea
```

**3. Use components:**
```tsx
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';

const ChatUI = () => {
  return (
    <div>
      <Avatar>
        <AvatarImage src="/avatar.png" />
        <AvatarFallback>AI</AvatarFallback>
      </Avatar>

      <Textarea placeholder="Type a message..." />

      <Button>Send</Button>
    </div>
  );
};
```

---

## Figma & Design Resources

### Official Figma Templates

1. **ChatGPT UI Kit by SnowUI**
   - Link: https://www.figma.com/community/file/1226866936281840601/chatgpt-ui-kit-ai-chat
   - Features: Multi-terminal responsive (desktop, tablet, mobile)
   - Design system included

2. **Ultimate ChatGPT UI Kit**
   - Link: https://www.figma.com/community/file/1281307509427695706/ultimate-chatgpt-ui-kit
   - Features: Figma Variables, robust design system
   - Comprehensive component library

3. **Free ChatGPT-4o UI Kit**
   - Link: https://www.figma.com/community/file/1382664631777133030/free-chatgpt-4o-ui-kit
   - Features: Interactive components, light/dark mode variables
   - Based on GPT-4o interface

4. **OpenAI ChatGPT Free UI Kit (Recreated)**
   - Link: https://www.figma.com/community/file/1235720165777081680/openai-chatgpt-free-ui-kit-recreated
   - Features: Recreation of actual ChatGPT interface
   - Free and customizable

5. **ChatGPT Redesign with ShadCN/UI Components**
   - Link: https://www.figma.com/community/file/1406309259377756650/chatgpt-redesign-with-shadcn-ui-components
   - Features: Enhanced usability and aesthetics
   - shadcn/ui component integration

### Design System Tools

- **shadcn/ui Blocks:** https://www.shadcn.io/blocks (AI chatbot block available)
- **LangUI:** https://github.com/LangbaseInc/langui (60+ AI-specific components)
- **Horizon UI Boilerplate:** https://horizon-ui.com/docs-boilerplate/shadcn-components/chat

---

## References & Links

### Top GitHub Repositories

1. **LibreChat** - https://github.com/danny-avila/LibreChat
2. **BetterChatGPT** - https://github.com/ztjhz/BetterChatGPT
3. **Chatbot UI** - https://github.com/mckaywrigley/chatbot-ui
4. **LangUI** - https://github.com/LangbaseInc/langui
5. **chat-components** - https://github.com/miskibin/chat-components
6. **react-chat-stream** - https://github.com/XD2Sketch/react-chat-stream
7. **Every ChatGPT GUI** - https://github.com/billmei/every-chatgpt-gui (Comprehensive list)

### Technical Articles & Tutorials

**Streaming Implementation:**
- "How to build the ChatGPT typing animation in React" - https://dev.to/stiaanwol/how-to-build-the-chatgpt-typing-animation-in-react-2cca
- "ChatGPT clone with React Suspense and Streaming" - https://dev.to/fibonacid/chatgpt-clone-with-react-suspense-and-streaming-11me
- "Why React Apps Lag With Streaming Text" - https://akashbuilds.com/blog/chatgpt-stream-text-react

**UI Implementation:**
- "How to Build and Deploy a ChatGPT Clone" - https://kinsta.com/blog/chatgpt-clone/
- "Build Your Own ChatGPT Clone" - https://www.sitepoint.com/build-chatgpt-clone-react-openai-api/
- "Integrating ChatGPT With ReactJS" - https://dzone.com/articles/integrating-chatgpt-with-reactjs-a-comprehensive-g

**Markdown & Code Highlighting:**
- "Add Markdown & Code Syntax Highlighting" - https://www.alfianlosari.com/posts/add-markdown-and-code-syntax-higlighting-chatgpt-swiftui-ios-app/
- react-markdown documentation - https://github.com/remarkjs/react-markdown
- highlight.js - https://highlightjs.org/

**Design Patterns:**
- "Empty State UX examples" - https://www.eleken.co/blog-posts/empty-state-ux
- "Auto-Growing Inputs & Textareas" - https://css-tricks.com/auto-growing-inputs-textareas/
- "Dark Mode with CSS Variables" - https://dev.to/ditarahma08/dark-mode-with-css-variable-1p57

### Component Libraries & Tools

**shadcn/ui:**
- Official site: https://www.shadcn.io
- AI chatbot block: https://www.shadcn.io/blocks/ai-chatbot
- AI components: https://www.shadcn.io/ai

**Tailwind CSS:**
- Official docs: https://tailwindcss.com
- Dark mode: https://tailwindcss.com/docs/dark-mode

**React Ecosystem:**
- React 18: https://react.dev
- TypeScript: https://www.typescriptlang.org
- Vite: https://vitejs.dev
- Next.js: https://nextjs.org

### Icon Libraries

- **Lucide React:** https://lucide.dev (Recommended - clean, consistent)
- **Heroicons:** https://heroicons.com (Tailwind's icon library)
- **React Icons:** https://react-icons.github.io/react-icons

### OpenAI Resources

- **OpenAI API Docs:** https://platform.openai.com/docs
- **Chat Completions API:** https://platform.openai.com/docs/api-reference/chat
- **Streaming:** https://platform.openai.com/docs/api-reference/streaming

---

## Implementation Checklist

### Phase 1: Core UI (Week 1)
- [ ] Set up React + TypeScript + Tailwind project
- [ ] Install shadcn/ui and configure
- [ ] Create basic layout (sidebar + main area)
- [ ] Implement responsive sidebar (collapsible)
- [ ] Build message components (user + assistant)
- [ ] Add auto-resize textarea input
- [ ] Implement basic styling and spacing

### Phase 2: Functionality (Week 2)
- [ ] Integrate markdown rendering (react-markdown)
- [ ] Add syntax highlighting for code blocks
- [ ] Implement copy to clipboard functionality
- [ ] Add message streaming animation
- [ ] Build typing indicator (three dots)
- [ ] Create empty state with suggestions
- [ ] Add error handling and display

### Phase 3: Advanced Features (Week 3)
- [ ] Implement conversation history (sidebar)
- [ ] Add new chat functionality
- [ ] Build settings/profile menu
- [ ] Add dark/light mode toggle
- [ ] Implement stop generating button
- [ ] Add regenerate response feature
- [ ] Create message action buttons

### Phase 4: Polish & Optimization (Week 4)
- [ ] Optimize streaming performance (buffering)
- [ ] Add smooth animations and transitions
- [ ] Implement responsive mobile design
- [ ] Add keyboard shortcuts
- [ ] Test accessibility (a11y)
- [ ] Performance testing and optimization
- [ ] Cross-browser testing

### Phase 5: Energy Compliance Integration
- [ ] Customize branding for Nemo
- [ ] Add energy compliance-specific features
- [ ] Integrate with Nemo backend
- [ ] Add document upload/analysis
- [ ] Implement compliance-specific templates
- [ ] Add export functionality for reports

---

## Summary & Recommendations

### For 90%+ Accuracy Clone

**Use this stack:**
```
React 18 + TypeScript
+ Tailwind CSS
+ shadcn/ui
+ react-markdown
+ highlight.js
+ Lucide Icons
```

**Start with:**
1. **LibreChat** as reference for overall architecture
2. **shadcn/ui chatbot block** for core components
3. **BetterChatGPT** for clean, minimal implementation

**Key Success Factors:**
1. **Spacing is critical** - Use exact padding/margins (16px, 24px, etc.)
2. **Streaming performance** - Buffer tokens, update every 30-50ms, not every token
3. **Responsive design** - Mobile-first, test on real devices
4. **Markdown rendering** - Use react-markdown with proper code highlighting
5. **Dark mode** - Implement from day 1 using CSS variables
6. **Auto-resize textarea** - Essential for good UX
7. **Loading states** - Three dots animation, cursor for streaming
8. **Error handling** - Clear, actionable error messages

### Customization for Nemo Energy Compliance

**Additional features to add:**
- Energy compliance-specific prompt templates
- Document upload and analysis UI
- Compliance report generation and export
- Regulatory database search integration
- Multi-language support for international regulations
- Audit trail and conversation logging
- Role-based access control

---

**Report Compiled By:** Committee 1 - ChatGPT UI/UX Research
**Date:** November 20, 2025
**Total Pages:** Comprehensive
**Confidence Level:** High (90%+ accuracy achievable with provided resources)

**Next Steps:** Review this document with the development team and begin Phase 1 implementation using the recommended tech stack and resources.
