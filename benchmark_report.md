# Real Ticket Corpus Benchmark Report (claude-ops-agent)

Source: https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets/resolve/main/dataset-tickets-multi-lang-4-20k.csv (Hugging Face, public, real/scraped-style multilingual support tickets)

- Real English-language tickets sampled: 25
- Priority exact-match accuracy vs. real label ('urgent' counted as matching 'high'): 11/25 (44%)
- Predicted category distribution (no ground truth available for this repo's taxonomy - reported for manual review, not scored): {'technical_issue': 16, 'billing': 2, 'other': 7}

## Per-ticket detail

| Ticket | Subject | True priority | Predicted priority | Predicted category |
|---|---|---|---|---|
| RT-001 | Support for VR Headset (HTC Vive Cosmos) | low | high | technical_issue |
| RT-002 | Issues with Billing | low | high | billing |
| RT-003 | Enhancing Airtable for Marketing Efficiency | low | low | other |
| RT-004 | Incident Report Hadoop Issue | high | high | technical_issue |
| RT-005 | Reported Issue of Software Crashes | high | high | technical_issue |
| RT-006 | Django ElasticSearch HIPAA Compliance Concern | medium | urgent | technical_issue |
| RT-007 |  | high | urgent | billing |
| RT-008 | Report on Connectivity Problems | low | high | technical_issue |
| RT-009 |  | low | medium | other |
| RT-010 | Multiple Tools Experienced Concurrent Malfunctions | high | high | technical_issue |
| RT-011 | Support for Enhancing Digital Strategies and Brand | high | low | other |
| RT-012 | Report on Connectivity Problem | medium | high | technical_issue |
| RT-013 | Trouble with ClickUp Integration Smart-Thermometer | high | medium | technical_issue |
| RT-014 | Performance Concerns | medium | high | technical_issue |
| RT-015 | Enhancing Investment Strategies with KNIME | low | low | other |
| RT-016 | Issue with Medical Data Transmission | high | urgent | technical_issue |
| RT-017 | Problem with Investment Analytics | medium | high | technical_issue |
| RT-018 | Report on Failed Multiple Integrations | high | high | technical_issue |
| RT-019 | Alert: Possible Data Breach in Hospital Systems | medium | urgent | technical_issue |
| RT-020 | Security Breach in Healthcare Data | high | urgent | technical_issue |
| RT-021 | Irregular Data Reporting in Dynamics | medium | high | technical_issue |
| RT-022 | NZXT Marketing Support Inquiry | high | low | other |
| RT-023 | Strategies for Digital Brand Expansion with Multip | medium | low | other |
| RT-024 |  | medium | medium | other |
| RT-025 | Report of Security Breach in Hospital Systems | high | urgent | technical_issue |
