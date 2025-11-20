# Energy Compliance User Flow & Experience Design

## 1. User Personas (3 Total)

**Persona 1: Compliance Officer (Zhang Wei)**
Mid-level compliance officer managing regulatory risk across operations. Needs detailed regulations, precedent cases, and audit trails. Works under pressure—typical query time: 2-3 days. Prioritizes accuracy over speed. Tools: desktop (80%), mobile check-ins (20%).

**Persona 2: Project Manager (Li Ming)**
Oversees coal/energy transport projects. Needs quick go/no-go answers and realistic timelines. Searches 3-5 times per project. Time constraint: decisions required within hours. Delegates compliance details but needs executive summary. Tools: mobile-first (70%), desktop (30%).

**Persona 3: Operations Coordinator (Wang Hui)**
Day-to-day implementation handler. Executes compliance tasks—permits, inspections, documentation. Needs step-by-step guides and downloadable forms. Repeats similar queries. Least technical. Wants copy-paste solutions. Tools: desktop (90%), printed guides (offline).

---

## 2. Common Query Patterns (5 Examples)

1. **Transport/Logistics**: "How to transport 3 tons of coal through Shandong province? What permits needed?"
2. **Environmental Compliance**: "Which emissions standards apply to our natural gas facilities in Shanghai?"
3. **Safety/Labor**: "What safety certifications required for coal mine operations in Shanxi?"
4. **Licensing/Permits**: "Timeline and steps for obtaining coal trading license in Anhui?"
5. **Regional Differences**: "How do regulations differ for coal transport: Shandong vs. Inner Mongolia?"

---

## 3. Response Format Structure

- **Query Confirmation**: Restate user request + flag missing details
- **Executive Summary**: 2-3 sentence direct answer + compliance status (✓ Compliant/⚠ Risk)
- **Step-by-Step Guide**: Numbered process (1-15 steps max), with decision points
- **Required Documents**: Checkbox list of forms + deadlines + responsible department
- **Government Citations**: Source links + regulation codes + last updated date
- **Risk Warnings**: Non-compliance penalties, timing risks, regional blockers
- **Download Package**: Bundled forms, checklists, evidence templates (PDF)

---

## 4. Critical User Flows (3 Total)

### Flow 1: First-Time Complex Query Submission
1. User lands on search interface
2. Enter free-text query (e.g., "coal transport Shandong")
3. System returns query clarification panel (3-5 quick questions)
4. User selects relevant options (commodity type, quantity, route, timeline)
5. System displays response format: executive summary + step guide
6. User expands sections as needed (forms, citations, risks)
7. Download package or bookmark for later

### Flow 2: Follow-up / Refinement Query
1. User searches similar term (system suggests recent queries)
2. Select previous query template or modify criteria
3. System highlights changes from last answer (date updates, regulation changes)
4. User compares old vs. new requirements side-by-side
5. Download updated form package if changes exist
6. Mark as reviewed + track in personal compliance dashboard

### Flow 3: Document Implementation & Completion
1. User opens downloaded form package
2. Prefill common fields (company name, license number, contact)
3. Form wizard guides field-by-field (with inline examples from regulations)
4. Document validation: check for missing/invalid entries
5. Generate evidence checklist (what to submit to which agency)
6. Print, sign, and upload status to platform
7. Compliance tracker shows completion progress (0-100%)

---

## 5. Key UI Components

- **Query Input Box**: Auto-suggest based on history; support fuzzy matching (typos, regional names)
- **Query Clarification Panel**: Radio buttons + checkboxes (non-intrusive modal, not fullpage)
- **Response Card Stack**: Collapsible sections; accordion layout for deep reading
- **Risk Banner**: Prominent sticky warning (red/yellow) for non-compliance penalties or deadlines
- **Form Downloader**: One-click ZIP export; shows file count and estimated print pages
- **Citation Tooltip**: Hover-to-reveal regulation source, last updated date, confidence level
- **Compliance Dashboard**: Personal checklist tracker; overdue items flagged
- **Chat/Context Panel**: Quick clarification with AI (not replacement for official answers)
- **Mobile Responsive Grid**: 1-column layout on mobile; collapsible deep-dive sections
- **Print Optimizer**: Hidden CSS for clean PDF output; removes interactive elements

---

## 6. Trust Indicators (5 Items)

1. **Government Source Label**: Badge showing "Source: Shandong Dept. of Energy, 2025-11-15"
2. **Regulation Code Display**: Visible regulation codes (e.g., GB/T 2589-2020) with clickable links
3. **Last Updated Timestamp**: "Last verified: Nov 20, 2025" with refresh-check button
4. **Expert Reviewer Attribution**: "Reviewed by: Compliance Officer, Shandong Coal Bureau"
5. **Confidence Score**: Visual indicator (Green ✓ / Yellow ⚠ / Red ✗) for answer certainty

---

## 7. Success Metrics (5 KPIs)

1. **Task Completion Rate**: Target 90% of users complete their compliance query end-to-end (measure: form download + bookmark/export action)
2. **Time-to-Answer**: Median 90 seconds from query submission to executive summary display (P95: <3 minutes)
3. **Re-Query Reduction**: 30% fewer repeat queries by same user (measure: return visit with identical query vs. refined/new)
4. **Form Accuracy**: 85% of downloaded forms pass internal validation (missing fields flagged before submission)
5. **Support Ticket Deflection**: 70% reduction in compliance-related support tickets post-launch (measure: tickets vs. FAQs resolved in-platform)

---

## Design Priorities for 90% Completion
- **Clarity over features**: Remove jargon; use real regulation codes as proof, not as explanation
- **Mobile-first response format**: Mobile users should see executive summary + next step without scrolling
- **Pre-fill + templates**: Reuse previous queries; reduce user typing
- **Offline accessibility**: PDF/printable guides work without internet (critical for field staff)
- **Reassurance**: Every answer includes confidence level + contact info for escalation
