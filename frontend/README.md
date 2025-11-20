# Nemo Frontend - ChatGPT-Clone Interface

A modern, bilingual (Chinese/English) ChatGPT-style interface for the Nemo Energy Compliance platform with Nemo olive green branding.

## Features

- **ChatGPT-Clone UI**: Exact ChatGPT layout with sidebar, streaming messages, and full-width content
- **Bilingual Support**: Seamless switching between Chinese (中文) and English
- **Olive Green Branding**: Single-color olive green palette (no gradients), WCAG AA accessible
- **Persistent State**: Chat history and preferences saved to localStorage with Zustand
- **Real-time Updates**: Streaming responses with loading indicators
- **Citation Display**: Government document references with links
- **Responsive Design**: Mobile-friendly with Tailwind CSS

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management with persist middleware
- **React Markdown** - Markdown rendering with GFM support
- **Lucide React** - Icon library

## Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Environment Variables

Create a `.env` file:

```bash
# For local development (uses Vite proxy)
VITE_API_URL=/api

# For production (use your Cloud Function URL)
# VITE_API_URL=https://nemo-query-xxxxx.asia-east2.run.app
```

## Project Structure

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── Sidebar.tsx           # Chat history sidebar
│   │   ├── ChatArea.tsx          # Main chat display area
│   │   ├── ChatMessage.tsx       # Individual message component
│   │   ├── ChatInput.tsx         # Message input with auto-resize
│   │   ├── ContextSelectors.tsx  # Province & asset selectors
│   │   └── LanguageToggle.tsx    # Language switcher
│   ├── stores/            # Zustand stores
│   │   └── chatStore.ts          # Chat state management
│   ├── hooks/             # Custom React hooks
│   │   └── useLanguage.ts        # Language hook with persist
│   ├── lib/               # Utilities
│   │   ├── i18n.ts              # Translation system
│   │   ├── api.ts               # API client
│   │   └── utils.ts             # Helper functions
│   ├── types/             # TypeScript types
│   │   └── index.ts             # Type definitions
│   ├── App.tsx            # Main app component
│   ├── main.tsx           # Entry point
│   └── index.css          # Global styles
├── index.html             # HTML template
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind with olive colors
├── tsconfig.json          # TypeScript config
└── package.json           # Dependencies
```

## Color System

Nemo olive green brand colors (no gradients):

```css
--olive-500: #8B9456  /* PRIMARY BRAND COLOR */
--olive-600: #6F7A3E  /* Hover states */
--olive-700: #556B2F  /* Active states */
```

Full 11-shade olive scale available in `tailwind.config.js`.

## Development

```bash
# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## API Integration

The frontend communicates with the Nemo backend via POST requests:

```typescript
POST /api
Content-Type: application/json

{
  "province": "gd",
  "asset": "solar",
  "doc_class": "grid",
  "question": "并网验收需要哪些资料？",
  "lang": "zh"
}
```

Response format:

```typescript
{
  "answer_zh": "...",
  "citations": [
    {
      "title": "...",
      "url": "https://...",
      "effective_date": "2023-01-01"
    }
  ],
  "trace_id": "..."
}
```

## Deployment

### Option 1: Cloud Run (Recommended)

```bash
# Build production bundle
npm run build

# Deploy to Cloud Run
gcloud run deploy nemo-frontend \
  --source . \
  --region asia-east2 \
  --allow-unauthenticated \
  --set-env-vars="VITE_API_URL=https://nemo-query-xxxxx.asia-east2.run.app"
```

### Option 2: Google Cloud Storage + CDN

```bash
# Build for production
npm run build

# Upload to GCS bucket
gsutil -m cp -r dist/* gs://nemo-frontend/

# Configure bucket for static hosting
gsutil web set -m index.html -e index.html gs://nemo-frontend
```

## Customization

### Adding New Provinces

Edit `src/components/ContextSelectors.tsx`:

```typescript
const PROVINCES: Province[] = ['gd', 'sd', 'nm', 'bj'] // Add 'bj'
```

Add translation in `src/lib/i18n.ts`:

```typescript
provinces: {
  gd: '广东省',
  sd: '山东省',
  nm: '内蒙古自治区',
  bj: '北京市', // Add translation
}
```

### Adding New Assets

Edit `src/components/ContextSelectors.tsx`:

```typescript
const ASSETS: Asset[] = ['solar', 'coal', 'wind', 'hydro'] // Add 'hydro'
```

Add translation in `src/lib/i18n.ts`:

```typescript
assets: {
  solar: '光伏',
  coal: '煤电',
  wind: '风电',
  hydro: '水电', // Add translation
}
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

Proprietary - Nemo Energy Compliance Platform

## Support

For issues or questions, contact the Nemo development team.
