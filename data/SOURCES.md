# Data Sources

## Primary Datasets

### 1. OpenPoly Polymer Properties Database
- **What:** 741 polymers with 26 experimentally measured properties (Tg, Tm, Td, tensile strength, Young's modulus, elongation at break, etc.)
- **Source:** Wang Group, Fudan University (2025)
- **Paper:** https://link.springer.com/article/10.1007/s10118-025-3402-y
- **GitHub:** https://github.com/WangGroupFDU/Openpoly_benchmark
- **File:** `data/final_polymer_properties_fromliterature.csv`
- **Collection method:** Downloaded CSV from GitHub repository

### 2. Celgard Battery Separator Product Specifications
- **What:** 30 commercial separator products with specs (thickness, porosity, Gurley number, tensile strength, puncture strength, thermal shrinkage)
- **Source:** Celgard LLC (Asahi Kasei subsidiary)
- **URL:** https://www.celgard.com/product-data
- **Files:** `data/celgard_products.csv`, `data/celgard_specs.csv`, `data/celgard_pdfs/`
- **Collection method:** Web scraped product page with `requests` + `BeautifulSoup` (`scrape_celgard.py`), then downloaded and parsed 30 PDF datasheets with `pdfplumber` (`scrape_celgard_pdfs.py`)

## Scraped Literature Sources

Tables scraped from open-access PMC review articles using `requests` + `BeautifulSoup` (`scrape_literature.py`). Total: 337 rows from 19 tables across 7 articles.

### 3. PMC10534950 — "Engineering Polymer-Based Porous Membrane for Sustainable LIB Separators"
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC10534950/
- **Journal:** Polymers, 2023
- **Tables scraped:** 1 (33 rows — multi-polymer comparison with thermal shrinkage, porosity, ionic conductivity)
- **File:** `data/literature_PMC10534950_table7.csv`

### 4. PMC11241740 — "Eco-Friendly Lithium Separators: A Comprehensive Review of Cellulose-Based Materials"
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11241740/
- **Journal:** Polymers, 2024
- **Tables scraped:** 3 (55 rows — cross-polymer comparison including cellulose, PE, PP, PVDF, PET with thermal stability, tensile strength, cost)
- **Files:** `data/literature_PMC11241740_table0.csv`, `_table1.csv`, `_table2.csv`

### 5. PMC11511470 — "Electrospun PVDF-Based Separators for Lithium-Ion Batteries"
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11511470/
- **Journal:** Membranes, 2024
- **Tables scraped:** 5 (54 rows — PVDF and variant separator properties by electrospinning method)
- **Files:** `data/literature_PMC11511470_table0.csv` through `_table4.csv`

### 6. PMC6161240 — "Recent Advances in PVDF and Its Copolymers for Li-Ion Battery Separators"
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC6161240/
- **Journal:** Materials, 2018
- **Tables scraped:** 5 (143 rows — PVDF variants: pure, coated, composite, filled, and blended separators with porosity, conductivity, capacity)
- **Files:** `data/literature_PMC6161240_table0.csv` through `_table5.csv`

### 7. PMC12073824 — "Polyphenylene Sulfide (PPS) Separators for Lithium-Ion Batteries"
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC12073824/
- **Journal:** Polymers, 2025
- **Tables scraped:** 1 (14 rows — PPS separator variants by process method)
- **File:** `data/literature_PMC12073824_table0.csv`

### 8. PMC7831081 — "Li-Ion Battery Separators Based on Electrospun Nanofibers: Safety and Modelling"
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC7831081/
- **Journal:** Membranes, 2021
- **Tables scraped:** 2 (29 rows — separator requirement specs, mechanical properties)
- **Files:** `data/literature_PMC7831081_table1.csv`, `_table4.csv`

### 9. PMC7603034 — "A Review of Functional Separators for Lithium Metal Battery Applications"
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC7603034/
- **Journal:** Journal of Power Sources, 2020
- **Tables scraped:** 1 (5 rows — separator performance data)
- **File:** `data/literature_PMC7603034_table0.csv`

## Additional Literature References (safety label assignment)

Safety classifications for 42 known separator polymers were assigned based on thermal shutdown/meltdown data from the sources above plus:

### 10. Lagadec et al. (2019) — Nature Energy
- "Characterization and performance evaluation of lithium-ion battery separators"
- https://www.nature.com/articles/s41560-018-0295-9
- PE/PP/trilayer thermal shutdown and meltdown temperatures

### 11. NASA NTRS — "Battery Separator Characterization and Evaluation Procedures"
- https://ntrs.nasa.gov/citations/20100021170
- PE, PP shutdown/meltdown temperature validation

### 12. NASA NTRS — "Properties and Performance Attributes of Novel Co-extruded Polyolefin Battery Separator Materials"
- https://ntrs.nasa.gov/citations/20140002501

### 13. NASA NTRS — "Mechanical Properties of Battery Separator Materials Part 1"
- https://ntrs.nasa.gov/citations/20110008276

### 14. Electrochem Society Interface (2012)
- "The Role of Separators in Lithium-Ion Cell Safety"
- https://www.electrochem.org/dl/interface/sum/sum12/sum12_p061_065.pdf
- Thermal shutdown/meltdown reference values

### 15. TA Instruments — Battery Separator Thermal Analysis Application Note
- https://www.tainstruments.com/pdf/literature/TA457.pdf

### 16. PMC9063013 — Polysulfonamide/PAN Composite Separator
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9063013/

### 17. PMC10140945 — Polyimidobenzimidazole Nanofiber Separator
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10140945/

### 18. PMIA/Aramid Separator — Ionics (2020)
- https://link.springer.com/article/10.1007/s11581-020-03699-y

### 19. PBS Thermal Shutdown Separator — ACS Applied Nano Materials (2024)
- https://pubs.acs.org/doi/10.1021/acsanm.4c06653

### 20. PEEK Nanofiber Separator — Chinese Journal of Polymer Science (2023)
- https://link.springer.com/article/10.1007/s10118-023-3002-7

### 21. PBI Separator — ACS Applied Materials & Interfaces (2017)
- https://pubs.acs.org/doi/abs/10.1021/acsami.6b16316

### 22. Chitosan Nanofiber Separator — Polymers (2023)
- https://www.mdpi.com/2073-4360/15/18/3654

### 23. Chitin Nanofiber Separator — ACS Nano Letters (2017)
- https://pubs.acs.org/doi/abs/10.1021/acs.nanolett.7b01875

### 24. Silk Fibroin/Sericin Separator — J. Colloid Interface Sci. (2021)
- https://www.sciencedirect.com/science/article/abs/pii/S0021979721022049

### 25. Cellulose Derivative Separators — Materials Science for Energy Tech. (2020)
- https://www.sciencedirect.com/science/article/pii/S2666893920300013

### 26. PVDF-CTFE Separator — RSC Advances (2015)
- https://pubs.rsc.org/en/content/articlelanding/2015/ra/c5ra19335d

### 27. EVA/PEEK/EVA Separator — J. Membrane Science (2023)
- https://www.sciencedirect.com/science/article/abs/pii/S0376738823007159

### 28. Northwestern University Student Report — Battery Separator Comparison
- https://msecore.northwestern.edu/390/2022/Group3_Battery_Separators.pdf

### 29. ChemSusChem (2022) — "Thermal-Stable Separators"
- https://chemistry-europe.onlinelibrary.wiley.com/doi/10.1002/cssc.202201464

### 30. Videleaf (2024) — "Advances in LIB Separators: Engineering Polymeric Porous Membranes"
- https://videleaf.com/wp-content/uploads/2024/05/Advances-in-Lithium-Ion-Battery-Separators-A-Review-of-Engineering-Polymeric-Porous-Membranes.pdf

## Safety Label Definitions

| Label    | Criterion                                      |
|----------|-------------------------------------------------|
| safe     | Maintains structural integrity above 150°C      |
| marginal | Structural integrity between 120-150°C          |
| fail     | Loses structural integrity below 120°C          |
