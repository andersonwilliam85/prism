# Consulting Firm Config

**For:** Consulting firms & agencies  
**Example:** Tech consulting, design agencies, professional services  
**Hierarchy:** Organized by clients  

## What's Included

- **Multi-client support:** Switch contexts easily
- **Time tracking:** Billable hours integration
- **Client isolation:** Separate configs per client
- **Consultant ID:** Track who's on what project
- **Flexible:** Each client has different requirements

## User Info Fields

- Full Name
- Company Email
- Consultant ID
- Primary Client
- Time Tracking System (optional)

## Structure

```
Consulting Firm (base)
└── Clients
    ├── FinTech Client
    │   ├── Tools: Specific to finance
    │   └── Compliance: SOX, PCI-DSS
    │
    ├── Healthcare Client
    │   ├── Tools: HIPAA compliant
    │   └── Compliance: HIPAA, HITECH
    │
    └── Retail Client
        ├── Tools: E-commerce focused
        └── Compliance: PCI-DSS
```

## Installation

```bash
python3 scripts/package_manager.py install consulting-firm-config
python3 install-ui.py
# Select your primary client
```

## Features

### Per-Client Configuration

Each client gets:
- Custom tool requirements
- Specific compliance rules
- Client-specific repos
- NDA/security requirements

### Time Tracking

Integration with:
- Harvest
- Toggl
- Clockify
- Custom systems

### Context Switching

Easily switch between client projects with different:
- Git configs
- Cloud accounts
- Access credentials
- Compliance requirements

## Perfect For

- Consulting firms
- Design agencies
- Professional services
- Contract developers
- Multi-client agencies
