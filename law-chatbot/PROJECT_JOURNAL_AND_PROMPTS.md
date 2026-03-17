# Project Journal and Prompt Bank

## 1) Project Journal (Sample)

### Day 1 - Setup
- Created backend with Django + DRF.
- Created frontend with React + Vite.
- Added basic chat session and query models.

### Day 2 - Async Pipeline
- Integrated Celery worker and Redis broker.
- Query submission now runs in background task.
- Added status flow: pending -> completed.

### Day 3 - RAG Integration
- Added `legal_sections.csv` as knowledge source.
- Built Chroma vector store and retrieval logic.
- Integrated Ollama for LLM generation.

### Day 4 - Query Understanding
- Added typo correction and phrase normalization.
- Added intent-aware legal retrieval scoring.
- Added curated mappings for common legal complaints.

### Day 5 - Output Standardization
- Enforced strict output format:
  - LAW
  - SECTION
  - PUNISHMENT
  - NEXT STEPS
  - DISCLAIMER
- Added fallback text when punishment is procedural/not directly penal.

### Day 6 - Data and Quality Checks
- Audited law dataset completeness.
- Verified all curated law pick rules exist in dataset.
- Generated full law annexure file: `ALL_LAWS.md`.

### Day 7 - Final Polish
- Improved theft mapping (`IPC 379`, `IPC 380`) for better punishment output.
- Improved salary/incentive mapping to specific wage law reference.
- Prepared viva notes and prompt bank.

---

## 2) Prompt Bank (For Demo and Testing)

## A) Criminal
1. bike stolen near bus stand
2. theft in my home at night
3. chain snatching in market
4. someone threatened me on call
5. harassment in college campus
6. bad touch complaint
7. stalking by unknown person
8. rape complaint procedure

## B) Cyber
9. online scam via UPI payment
10. whatsapp fraud money taken
11. fake instagram account using my photo
12. private photos leaked online
13. phishing link and bank OTP fraud

## C) Labour / Employment
14. salary not paid for 2 months
15. company not giving my pending wages
16. unlawful deduction from salary
17. company does not provide incentive to me
18. private company terminated me unfairly

## D) Civic / Municipal
19. no road in my street
20. pothole problem in my area
21. drainage overflow near my house
22. garbage not collected in my ward
23. street light not working complaint
24. water supply issue in street

## E) Property / Family
25. neighbor encroached my land
26. property boundary dispute
27. house owner forcing tenant to vacate
28. landlord denied water supply
29. family land partition dispute

## F) Women / Child / Elder Safety
30. dowry harassment by husband family
31. domestic violence help
32. child abuse complaint under pocso
33. senior citizen maintenance complaint

---

## 3) Expected Output Template (Must Follow)

LAW: <Act/IPC + Section>
SECTION: <Section title>
PUNISHMENT: <Penalty or procedural remedy>
NEXT STEPS: 1... 2... 3...
DISCLAIMER: Consult lawyer

---

## 4) Viva Quick Q&A

### Q: Why Celery?
A: AI and retrieval calls may take time; Celery keeps API responsive and processes queries asynchronously.

### Q: Why RAG?
A: It grounds LLM answers in project legal dataset and reduces random responses.

### Q: How consistency is ensured?
A: Backend normalizes all responses into strict 5-line legal format.

### Q: How many laws are covered?
A: Current project dataset has 183 unique law entries (see `ALL_LAWS.md`).

### Q: Is this final legal advice?
A: No. It gives first-level guidance; final decision should be with a qualified lawyer.