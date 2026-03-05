# University Config

**For:** Universities & educational institutions  
**Example:** Research universities, computer science departments  
**Hierarchy:** Departments → Labs  

## What's Included

- **Academic structure:** Departments and research labs
- **Student support:** GitHub Education Pack integration
- **Research tools:** HPC clusters, specialized software
- **Role-based:** Students, professors, researchers
- **Advisor tracking:** Connect students with advisors

## User Info Fields

- Full Name
- University Email (@university.edu)
- Student/Employee ID
- Role (Student, Professor, Researcher)
- Department
- Advisor/Supervisor (optional)

## Structure

```
University (base)
└── Departments
    ├── Computer Science
    │   └── Labs
    │       ├── Machine Learning Lab
    │       ├── Systems & Networking Lab
    │       └── Security Research Lab
    │
    └── Data Science
        └── Labs
            ├── Big Data Lab
            └── Visualization Lab
```

## Installation

```bash
python3 scripts/package_manager.py install university-config
python3 install-ui.py
# Select your department and lab
```

## Features

### For Students

- GitHub Education Pack (free tools!)
- Access to university HPC clusters
- Course-specific software
- Collaboration tools
- Learning resources

### For Professors

- Research computing resources
- Grant management tools
- Publication tracking
- Course management

### For Researchers

- High-performance computing
- Specialized software (MATLAB, R, etc.)
- Data storage
- Collaboration platforms

### Resources

- University library access
- Academic journals
- Research databases
- Computing clusters
- Lab-specific tools

## Perfect For

- Universities
- Research institutions
- Computer science departments
- Engineering schools
- Academic research labs
