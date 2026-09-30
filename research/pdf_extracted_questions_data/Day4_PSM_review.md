# Day 4 PSM source review

Reviewed on 2026-09-30 against `Day4 PSM.pdf`: 155 viewer pages, with p.155 blank.
All 38 questions, answer letters and cited source pages were checked against
extracted text and rendered handwritten tables/figures. No answer-letter
transcription error was found. This bank samples five chapters; it does not
cover every examinable fact in the PDF.

| Item | Correction | Evidence |
| --- | --- | --- |
| Ingestion report | Corrected 154 to 155 pages and identified the blank final page. Removed broken ChatGPT citation markers. | Local PDF metadata and rendered pp.154–155 |
| Q2 | Attached a tight crop of the upper-left scatter plot, with no handwritten answer label. | PDF p.32 |
| Q3 | Described Saheli and Chhaya as contraceptives containing ormeloxifene, rather than implying that one brand was simply renamed. | PDF p.69; [NHM oral-pill manual](https://www.nhm.gov.in/images/pdf/programmes/family-planing/guidelines/Reference_Manual_Oral_Pills.pdf) |
| Q8–9 | Specified India’s rural public-health facilities and secondary referral care. Removed the universal claim that every CHC is a designated First Referral Unit. | PDF p.88; [IPHS CHC guidance](https://www.nhm.gov.in/images/pdf/guidelines/iphs/iphs-revised-guidlines-2022/02-CHC_IPHS_Guidelines-2022.pdf), which distinguishes FRU and non-FRU CHCs |
| Q14 | Corrected finished-polymer/PVC terminology to occupational vinyl chloride monomer exposure during manufacture. | PDF p.114; [NCI vinyl chloride](https://www.cancer.gov/about-cancer/causes-prevention/risk/substances/vinyl-chloride) |
| Q17 | Specified the Census of India’s females-per-1,000-males convention. | PDF p.137 |
| Q19 | Added equal variances to the independent, normally distributed groups for the conventional ANOVA choice. | PDF p.19 |
| Q20 | Corrected the explanation for the distractor 8: it uses four rather than three as the column factor. | PDF p.23; (3−1)(4−1)=6 |
| Q21 | Replaced “accepting a false null” with “failing to reject a false null” in the Type II explanation. | PDF p.40 |
| Q25 | Kept the ANM association while recognizing ASHA’s broader interface with the public-health system; standardized options as health-worker roles. | PDF p.93; [NHM ASHA role](https://www.nhm.gov.in/nhm/about-nhm/index1.php?lang=1&level=1&lid=226&sublinkid=150) |
| Q28 | Specified carcinogenic aromatic amines such as benzidine in dye-industry exposure. | PDF p.114; [NCI bladder-cancer risk](https://www.cancer.gov/types/bladder/hp/bladder-screening-pdq) |
| Q31 | Specified annual births and the midyear population denominator for GFR. | PDF p.143; 240/12,000 × 1,000 = 20 |
| Q34 | Specified independent random samples and standard error of the mean. | PDF pp.9,11; SD/√100 is half SD/√25 |
| Q35 | Replaced raw before/after skewness as the test-selection rule with paired ordinal pain categories and directions of change, excluding ties. Updated the source citation to pp.7,19. A paired t-test depends on within-pair differences, so marginal skewness alone did not settle the original item. | [NIST sign test](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/signtest.htm); [NIST paired observations](https://www.itl.nist.gov/div898/handbook/prc/section3/prc311.htm) |
| Q36–37 | Confirmed the existing keys: CuT 380A up to 10 years, CuT 375 up to 5 years, and routine Antara reinjection at 3 months/13 weeks. Removed explanation wording that pointed back at the notes. | PDF pp.65,69; [NHM IUCD manual](https://www.nhm.gov.in/New_Updates_2018/NHM_Components/RMNCHA/Family_planning/Schemes_%26_Guidelines/IUCD/IUCD_Manual_English.pdf); [NHM injectable MPA manual](https://www.nhm.gov.in/New_Updates_2018/NHM_Components/RMNCHA/Family_planning/Schemes_%26_Guidelines/Injectable_Contraceptive_MPA.pdf) |
| Q38 | Confirmed SRS’s dual-record method and infant-mortality estimates. | PDF p.140; [ORGI vital statistics](https://www.censusindia.gov.in/census.website/en/node/180) |

All 38 answer letters are retained. The bank has 17 Tier 1, 16 Tier 2 and
5 Tier 3 questions, with one image. Strict lint reports zero errors and two
non-blocking warnings: Q28’s correct option is longer than the distractors;
Q19 and Q35 share several statistical-test options. The original tier labels
are retained, not calibrated to official examination difficulty.

## Captures and limits

Open Web Search’s daemon timed out during the Day 1 investigation; built-in web
search and primary-source retrieval supplied the fallback for both reviews.
Khiip successfully archived:

- NIST sign test: `01M3SK2G7ZVP1SAAHA4SXCZ260`, `captures/web/sign-test.md`.
- NCI vinyl chloride: `01M3SK2H2PT5MAR8PV28FSR16V`, `captures/web/vinyl-chloride-cancer-causing-substances.md`.
- NHM ASHA role: `01M3SK85W892WN6TE63WVEJ1B6`, `captures/web/about-accredited-social-health-activist-asha-national-health-mission.md`.

Capture paths are relative to `/home/hamza/khiip-vault/`. The IPHS PDF capture
request timed out after 55 seconds; archival is unconfirmed. The ORGI web-page
capture failed with an upstream certificate-verification error. Both sources
were available through web retrieval; no successful Khiip capture is claimed.
Other linked primary references were retrieved through web tools, not archived.
