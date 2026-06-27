"""Generate sample legislative PDFs for testing the Assembly-KB ingestion pipeline.

Creates documents across three languages, multiple categories, and security levels
in data/sample_docs/ with sub-folders per state.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fpdf import FPDF

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_docs"

# ── Document definitions ────────────────────────────────────────────────────

DOCUMENTS = [
    # ── English – Andhra Pradesh ────────────────────────────────────────────
    {
        "folder": "AP",
        "filename": "AP_Appropriation_Bill_2025_EN.pdf",
        "language": "en",
        "title": "Andhra Pradesh Appropriation Bill, 2025",
        "category": "BILL",
        "security": "PUBLIC",
        "content": [
            "ANDHRA PRADESH APPROPRIATION BILL, 2025",
            "(Bill No. 14 of 2025)",
            "",
            "A Bill to authorise payment and appropriation of certain sums from and out of the "
            "Consolidated Fund of the State of Andhra Pradesh for the services of the financial "
            "year 2025-26.",
            "",
            "BE it enacted by the Legislature of the State of Andhra Pradesh in the Seventy-sixth "
            "Year of the Republic of India as follows:",
            "",
            "1. Short title: This Act may be called the Andhra Pradesh Appropriation Act, 2025.",
            "",
            "2. Withdrawal of Rs. 2,76,432 crore from the Consolidated Fund:",
            "From and out of the Consolidated Fund of the State of Andhra Pradesh there may be "
            "paid and applied sums not exceeding those specified in column 3 of the Schedule "
            "amounting in the aggregate to the sum of Two Lakh Seventy-Six Thousand Four Hundred "
            "and Thirty-Two Crore Rupees towards defraying the several charges which will come "
            "in course of payment during the financial year 2025-26.",
            "",
            "SCHEDULE",
            "1. Revenue Department - Rs. 8,450 Crore",
            "2. Agriculture Department - Rs. 12,300 Crore",
            "3. Education Department - Rs. 24,560 Crore",
            "4. Health and Family Welfare - Rs. 18,900 Crore",
            "5. Roads and Buildings - Rs. 15,200 Crore",
            "6. Irrigation and Water Resources - Rs. 22,000 Crore",
            "7. Rural Development - Rs. 16,800 Crore",
            "8. Urban Development - Rs. 9,500 Crore",
            "9. Social Welfare - Rs. 14,200 Crore",
            "10. Police and Home Affairs - Rs. 7,800 Crore",
            "",
            "3. Appropriation: The sums authorised to be paid and applied from and out of the "
            "Consolidated Fund of the State by this Act shall be appropriated for the services "
            "and purposes expressed in the Schedule in relation to each grant.",
        ],
    },
    {
        "folder": "AP",
        "filename": "AP_Assembly_Debate_Budget_Session_2025_EN.pdf",
        "language": "en",
        "title": "AP Assembly Debate – Budget Session 2025",
        "category": "DEBATE_TRANSCRIPT",
        "security": "PUBLIC",
        "content": [
            "ANDHRA PRADESH LEGISLATIVE ASSEMBLY",
            "Official Debate Transcript",
            "Budget Session 2025 – Day 3",
            "Date: 15th March 2025",
            "",
            "HON'BLE SPEAKER: The House will now take up the discussion on the Budget for "
            "the year 2025-26. The Finance Minister may present the general discussion.",
            "",
            "FINANCE MINISTER: Thank you, Hon'ble Speaker. I rise to present before this "
            "august House the budget estimates for the financial year 2025-26.",
            "",
            "The total budget estimate is Rs. 2,76,432 Crore, representing a 12.4% increase "
            "over the revised estimates of the previous year.",
            "",
            "Key allocations:",
            "- Amma Vodi Scheme: Rs. 6,500 Crore for educational support",
            "- YSR Rythu Bharosa: Rs. 4,200 Crore for farmer income support",
            "- Jagananna Vasathi Deevena: Rs. 3,100 Crore for student fee reimbursement",
            "- Nadu-Nedu Phase 3: Rs. 2,800 Crore for school infrastructure",
            "",
            "LEADER OF THE OPPOSITION: Mr. Speaker, while we welcome the increased "
            "allocation for education, we note that the irrigation sector has seen a "
            "decrease of 3.2% compared to last year. The Polavaram project needs "
            "additional funding of at least Rs. 5,000 Crore to meet the revised deadline.",
            "",
            "MEMBER FROM VIJAYAWADA: Sir, the allocation for the capital region development "
            "is insufficient. We request the government to provide dedicated funding for the "
            "Amaravati Capital City project.",
            "",
            "HON'BLE SPEAKER: The discussion will continue tomorrow. The House is adjourned "
            "until 11:00 AM tomorrow.",
        ],
    },
    {
        "folder": "AP",
        "filename": "AP_Committee_Report_Water_Resources_EN.pdf",
        "language": "en",
        "title": "Committee Report on Water Resources – AP",
        "category": "COMMITTEE_REPORT",
        "security": "RESTRICTED",
        "content": [
            "ANDHRA PRADESH LEGISLATIVE ASSEMBLY",
            "STANDING COMMITTEE ON WATER RESOURCES",
            "Report No. 47 / 2025",
            "CONFIDENTIAL – FOR COMMITTEE MEMBERS AND AUTHORIZED PERSONNEL ONLY",
            "",
            "Subject: Status of Major and Medium Irrigation Projects in Andhra Pradesh",
            "",
            "1. INTRODUCTION",
            "This committee was constituted under Rule 277 of the Rules of Procedure of the "
            "Andhra Pradesh Legislative Assembly to examine the status of ongoing irrigation "
            "projects and recommend measures for expediting completion.",
            "",
            "2. PROJECTS UNDER REVIEW",
            "2.1 Polavaram Irrigation Project:",
            "   - Estimated Cost: Rs. 55,548.87 Crore (Revised)",
            "   - Expenditure to date: Rs. 38,200 Crore",
            "   - Physical Progress: 72.3%",
            "   - Issues: Land acquisition disputes in 7 mandals, rehabilitation of 105 villages",
            "",
            "2.2 Vamsadhara Project Phase-II:",
            "   - Estimated Cost: Rs. 3,850 Crore",
            "   - Expenditure to date: Rs. 1,200 Crore",
            "   - Status: Environmental clearance pending from MoEFCC",
            "",
            "2.3 Uttarandhra Sujala Sravanthi:",
            "   - Estimated Cost: Rs. 15,000 Crore",
            "   - Preliminary DPR stage",
            "",
            "3. COMMITTEE OBSERVATIONS",
            "The committee notes with concern that cost overruns have exceeded 40% in three "
            "major projects. The displacement of tribal communities remains inadequately "
            "addressed. Budget utilization stands at 68% against sanctioned amounts.",
            "",
            "4. RECOMMENDATIONS",
            "4.1 Immediate release of Rs. 8,000 Crore pending installment for Polavaram",
            "4.2 Fast-track environmental clearances through State-level SEIAA",
            "4.3 Establish dedicated monitoring cell with monthly progress reviews",
            "4.4 Complete R&R packages before further land acquisition",
        ],
    },
    # ── Telugu – Andhra Pradesh ─────────────────────────────────────────────
    {
        "folder": "AP",
        "filename": "AP_Press_Release_Education_TE.pdf",
        "language": "te",
        "title": "ఆంధ్రప్రదేశ్ ప్రభుత్వ ప్రకటన - విద్యా సంస్కరణలు",
        "category": "PRESS_RELEASE",
        "security": "PUBLIC",
        "unicode": True,
        "content": [
            "ఆంధ్రప్రదేశ్ ప్రభుత్వం - అధికారిక ప్రకటన",
            "విద్యా శాఖ (Education Department)",
            "తేదీ: 20-03-2025",
            "",
            "విషయం: ఆంధ్రప్రదేశ్ విద్యా సంస్కరణలను ప్రకటించడం",
            "",
            "ఆంధ్రప్రదేశ్ ప్రభుత్వం కొత్త విద్యా సంస్కరణ పథకాన్ని ప్రకటించింది.",
            "ఈ పథకం కింద క్రింది చర్యలు చేపడతాము:",
            "",
            "1. అమ్మ ఒడి పథకం - విద్యార్థుల తల్లి దండ్రులకు రూ. 15,000",
            "   ఆర్థిక సహాయం ప్రతీ సంవత్సరం అందించడం.",
            "",
            "2. నాడు-నేడు ఫేజ్ 3 - 45,000 పాఠశాలల అలంకరణలు మరియు",
            "   అభివృద్ధి పనులు.",
            "",
            "3. డిజిటల్ తరగతి గదులు - 10,000 పాఠశాలల్లో స్మార్ట్ క్లాస్ రూమ్",
            "   ఏర్పాటు చేయడం.",
            "",
            "4. ఉపాధ్యాయ శిక్షణ - 1,50,000 ఉపాధ్యాయులకు విశేష శిక్షణ",
            "   కార్యక్రమాలు నిర్వహించడం.",
            "",
            "5. జగనన్న విద్యా దీవెన - ఇంజనీరింగ్ మరియు మెడికల్",
            "   విద్యార్థులకు సంపూర్ణ ఫీజు రీయింబర్స్‌మెంట్.",
            "",
            "ఈ సంస్కరణల వల్ల 80 లక్షల మంది విద్యార్థులకు ప్రత్యక్ష లాభం",
            "చేకూరుతుంది. రాష్ట్ర విద్యా రంగంలో విప్లవాత్మక మార్పులు రావడం",
            "ఖాయం అని ముఖ్యమంత్రి హామీ ఇచ్చారు.",
            "",
            "ఆంధ్రప్రదేశ్ శాసనసభ అధికారిక ప్రకటన.",
        ],
    },
    {
        "folder": "AP",
        "filename": "AP_Assembly_Debate_Excerpt_TE.pdf",
        "language": "te",
        "title": "ఆంధ్రప్రదేశ్ శాసనసభ చర్చ - బడ్జెట్ సమావేశం",
        "category": "DEBATE_TRANSCRIPT",
        "security": "PUBLIC",
        "unicode": True,
        "content": [
            "ఆంధ్రప్రదేశ్ శాసనసభ",
            "అధికారిక చర్చా నివేదిక",
            "బడ్జెట్ సమావేశం 2025 - మూడవ రోజు",
            "తేదీ: 15 మార్చి 2025",
            "",
            "గౌరవ సభాపతి: సభ ఇప్పుడు 2025-26 సంవత్సరపు బడ్జెట్ పై",
            "చర్చను చేపడుతుంది. ఆర్థిక మంత్రి సాధారణ చర్చను ప్రవేశపెట్టవచ్చు.",
            "",
            "ఆర్థిక మంత్రి: ధన్యవాదాలు, గౌరవ సభాపతి గారు. నేను ఈ గౌరవ",
            "సభ ముందు 2025-26 ఆర్థిక సంవత్సరపు బడ్జెట్ అంచనాలను",
            "ప్రవేశపెడుతున్నాను.",
            "",
            "మొత్తం బడ్జెట్ అంచనా రూ. 2,76,432 కోట్లు, ఇది గత సంవత్సరం",
            "సవరించిన అంచనాల కంటే 12.4% పెరుగుదల.",
            "",
            "ముఖ్య కేటాయింపులు:",
            "- అమ్మ ఒడి పథకం: రూ. 6,500 కోట్లు",
            "- వైఎస్ఆర్ రైతు భరోసా: రూ. 4,200 కోట్లు",
            "- జగనన్న వసతి దీవెన: రూ. 3,100 కోట్లు",
            "- నాడు-నేడు ఫేజ్ 3: రూ. 2,800 కోట్లు",
            "",
            "ప్రతిపక్ష నాయకుడు: సభాపతి గారు, విద్యకు పెరిగిన కేటాయింపులను",
            "మేము స్వాగతిస్తున్నాము, కానీ నీటిపారుదల రంగం గత సంవత్సరంతో",
            "పోలిస్తే 3.2% తగ్గింది. పోలవరం ప్రాజెక్టుకు సవరించిన గడువుకు",
            "అదనంగా కనీసం రూ. 5,000 కోట్లు అవసరం.",
            "",
            "గౌరవ సభాపతి: చర్చ రేపు కొనసాగుతుంది. సభ రేపు ఉదయం",
            "11:00 గంటలకు వాయిదా వేయబడింది.",
        ],
    },
    {
        "folder": "AP",
        "filename": "AP_Committee_Report_Irrigation_TE.pdf",
        "language": "te",
        "title": "నీటిపారుదల ప్రాజెక్టులపై కమిటీ నివేదిక - ఆంధ్రప్రదేశ్",
        "category": "COMMITTEE_REPORT",
        "security": "RESTRICTED",
        "unicode": True,
        "content": [
            "ఆంధ్రప్రదేశ్ శాసనసభ",
            "నీటిపారుదల శాఖపై స్థాయీ సంఘం",
            "నివేదిక సంఖ్య 49 / 2025",
            "రహస్యం - కమిటీ సభ్యులకు మరియు అధికృత సిబ్బందికి మాత్రమే",
            "",
            "విషయం: ఆంధ్రప్రదేశ్‌లో ప్రధాన, మధ్యతరహా నీటిపారుదల ప్రాజెక్టుల స్థితి",
            "",
            "1. ఉపోద్ఘాతం",
            "ఆంధ్రప్రదేశ్ శాసనసభ నియమ నిబంధనల ప్రకారం 277వ నిబంధన కింద",
            "ఈ సంఘం ఏర్పాటు చేయబడింది. కొనసాగుతున్న నీటిపారుదల ప్రాజెక్టుల",
            "పురోగతిని పరిశీలించి, పూర్తి చేయడానికి సిఫార్సులు చేయడం దీని లక్ష్యం.",
            "",
            "2. సమీక్షలో ఉన్న ప్రాజెక్టులు",
            "2.1 పోలవరం నీటిపారుదల ప్రాజెక్టు:",
            "   - అంచనా వ్యయం: రూ. 55,548 కోట్లు (సవరించినది)",
            "   - ఇప్పటివరకు ఖర్చు: రూ. 38,200 కోట్లు",
            "   - భౌతిక పురోగతి: 72.3%",
            "   - సమస్యలు: 7 మండలాల్లో భూసేకరణ వివాదాలు, 105 గ్రామాల పునరావాసం",
            "",
            "2.2 వంశధార ప్రాజెక్టు దశ-2:",
            "   - అంచనా వ్యయం: రూ. 3,850 కోట్లు",
            "   - పర్యావరణ అనుమతి పెండింగ్‌లో ఉంది",
            "",
            "3. సంఘం పరిశీలనలు",
            "మూడు ప్రధాన ప్రాజెక్టులలో వ్యయం 40% మించిపోవడాన్ని సంఘం",
            "ఆందోళనతో గమనించింది. గిరిజన కుటుంబాల పునరావాసం ఇంకా",
            "సరిగా పరిష్కారం కాలేదు. బడ్జెట్ వినియోగం 68% వద్ద ఉంది.",
            "",
            "4. సిఫార్సులు",
            "4.1 పోలవరం కోసం పెండింగ్‌లో ఉన్న రూ. 8,000 కోట్లు వెంటనే విడుదల చేయాలి",
            "4.2 రాష్ట్రస్థాయి SEIAA ద్వారా పర్యావరణ అనుమతులను వేగవంతం చేయాలి",
            "4.3 నెలవారీ సమీక్షలతో ప్రత్యేక పర్యవేక్షణ విభాగాన్ని ఏర్పాటు చేయాలి",
            "",
            "ఈ నివేదిక శాసనసభ నియమావళి 275వ నిబంధన కింద రహస్యంగా",
            "వర్గీకరించబడింది. పంపిణీ గౌరవ సభాపతి మరియు శాసనసభ సభ్యులకు",
            "మాత్రమే పరిమితం.",
        ],
    },
    {
        "folder": "AP",
        "filename": "AP_Confidential_Cabinet_Note_TE.pdf",
        "language": "te",
        "title": "ఆంధ్రప్రదేశ్ - రహస్య కేబినెట్ నోట్",
        "category": "COMMITTEE_REPORT",
        "security": "CONFIDENTIAL",
        "unicode": True,
        "content": [
            "ఆంధ్రప్రదేశ్ ప్రభుత్వం",
            "మంత్రివర్గ కార్యదర్శి కార్యాలయం",
            "అత్యంత రహస్యం - సభాపతి కార్యాలయం మాత్రమే",
            "నోట్ సంఖ్య: CS/CONF/2025/14",
            "",
            "విషయం: శాసనసభ ప్రత్యేక సమావేశం - భద్రతా, వ్యూహాత్మక అంశాలు",
            "",
            "1. నేపథ్యం",
            "రాబోయే ప్రత్యేక సమావేశానికి సంబంధించి కింది రహస్య అంశాలను",
            "గౌరవ సభాపతి దృష్టికి తీసుకురావడం జరిగింది.",
            "",
            "2. ముఖ్య అంశాలు",
            "2.1 రాష్ట్ర ఆర్థిక పునర్వ్యవస్థీకరణ ప్రతిపాదన - రూ. 42,000 కోట్ల",
            "   అదనపు రుణ సమీకరణ. RBI అనుమతి పెండింగ్‌లో ఉంది.",
            "",
            "2.2 అంతర్రాష్ట్ర జల వివాదం - కృష్ణా నదీ జలాల కేటాయింపుపై",
            "   ట్రిబ్యునల్ ముందు రాష్ట్ర వాదనల వ్యూహం.",
            "",
            "2.3 సున్నితమైన శాంతిభద్రతల అంచనా - సమావేశ సమయంలో",
            "   అదనపు భద్రతా ఏర్పాట్లు అవసరం.",
            "",
            "3. సిఫార్సు",
            "ఈ అంశాలను సభలో ప్రస్తావించడానికి ముందు మంత్రివర్గ ఆమోదం",
            "పొందాలని సూచించడమైనది. పూర్తి వివరాలు అనుబంధంలో ఉన్నాయి.",
            "",
            "ఈ పత్రం అత్యంత రహస్యం. పంపిణీ గౌరవ సభాపతికి మాత్రమే పరిమితం.",
        ],
    },
    # ── English – Uttar Pradesh ─────────────────────────────────────────────
    {
        "folder": "UP",
        "filename": "UP_Industrial_Policy_Act_2025_EN.pdf",
        "language": "en",
        "title": "UP Industrial Development and Employment Act, 2025",
        "category": "ACT",
        "security": "PUBLIC",
        "content": [
            "UTTAR PRADESH INDUSTRIAL DEVELOPMENT AND EMPLOYMENT ACT, 2025",
            "(UP Act No. 8 of 2025)",
            "",
            "An Act to promote industrial development, attract investment, and generate "
            "employment in the State of Uttar Pradesh.",
            "",
            "WHEREAS it is expedient to consolidate and amend the law relating to industrial "
            "development, single window clearance, and land allotment for industrial purposes;",
            "",
            "BE IT ENACTED by the Legislature of the State of Uttar Pradesh as follows:",
            "",
            "CHAPTER I – PRELIMINARY",
            "1. Short title: This Act may be called the Uttar Pradesh Industrial Development "
            "and Employment Act, 2025.",
            "2. Commencement: It shall come into force on such date as the State Government "
            "may appoint by notification.",
            "",
            "CHAPTER II – INDUSTRIAL ZONES",
            "3. The State Government shall establish Special Industrial Zones in the following "
            "corridors:",
            "   (a) Noida-Greater Noida Industrial Corridor",
            "   (b) Lucknow-Kanpur Industrial Belt",
            "   (c) Agra-Mathura Manufacturing Hub",
            "   (d) Varanasi Textile and Handicraft Zone",
            "   (e) Prayagraj Knowledge and IT Park",
            "",
            "4. Land Allotment: Industrial land shall be allotted within 30 days of application "
            "through the single-window portal at concessional rates.",
            "",
            "CHAPTER III – INCENTIVES",
            "5. Tax incentives:",
            "   (a) 100% stamp duty exemption for 7 years",
            "   (b) SGST reimbursement up to 75% for 10 years",
            "   (c) Capital subsidy of 25% up to Rs. 50 Crore",
            "   (d) Employment generation subsidy of Rs. 5,000/month per new employee for 5 years",
            "",
            "CHAPTER IV – EMPLOYMENT",
            "6. Every industrial unit receiving incentives shall ensure minimum 50% of the "
            "workforce comprises domiciled residents of Uttar Pradesh.",
        ],
    },
    {
        "folder": "UP",
        "filename": "UP_Assembly_QA_Session_March_2025_EN.pdf",
        "language": "en",
        "title": "UP Assembly Question Hour – March 2025",
        "category": "QUESTION_ANSWER",
        "security": "PUBLIC",
        "content": [
            "UTTAR PRADESH VIDHAN SABHA",
            "Question Hour – Unstarred Questions",
            "Session: Budget Session 2025",
            "Date: 18th March 2025",
            "",
            "QUESTION NO. 2847",
            "Shri Rajesh Kumar (MLA, Varanasi South):",
            "Will the Minister of Health and Family Welfare be pleased to state:",
            "(a) The number of Primary Health Centres operational in Varanasi district;",
            "(b) The doctor-to-patient ratio in government hospitals;",
            "(c) Steps taken to address shortage of specialist doctors.",
            "",
            "ANSWER by Minister of Health:",
            "(a) There are 42 Primary Health Centres operational in Varanasi district as of "
            "January 2025. Out of these, 38 are functioning 24x7.",
            "(b) The doctor-to-patient ratio in Varanasi government hospitals is 1:1,800 "
            "against the WHO recommended ratio of 1:1,000.",
            "(c) The following steps have been taken:",
            "   - 150 MBBS seats added at BHU Medical College",
            "   - Walk-in interviews for specialist posts conducted monthly",
            "   - Telemedicine facility linked with AIIMS, New Delhi",
            "   - Rs. 200 Crore sanctioned for new medical equipment",
            "",
            "QUESTION NO. 2848",
            "Smt. Priya Singh (MLA, Lucknow Central):",
            "Will the Minister of Urban Development state the progress of the Lucknow Metro "
            "Phase 2 project?",
            "",
            "ANSWER by Minister of Urban Development:",
            "Lucknow Metro Phase 2 (Charbagh to Vasant Kunj, 12.4 km) is 64% complete. "
            "Civil work on 8 of 11 stations is finished. Track laying has commenced on the "
            "elevated section. Expected completion: December 2026. Total project cost: "
            "Rs. 5,100 Crore.",
        ],
    },
    {
        "folder": "UP",
        "filename": "UP_Gazette_Land_Revenue_2025_EN.pdf",
        "language": "en",
        "title": "UP Gazette Notification – Land Revenue Amendment",
        "category": "GAZETTE_NOTIFICATION",
        "security": "RESTRICTED",
        "content": [
            "UTTAR PRADESH GAZETTE",
            "EXTRAORDINARY",
            "PART 4 – SECTION (kha)",
            "Published by Authority",
            "No. 512/VII-V-1-1(ka)-32-2025  |  Lucknow, dated March 10, 2025",
            "",
            "REVENUE DEPARTMENT",
            "NOTIFICATION",
            "",
            "In exercise of the powers conferred by Section 33 of the Uttar Pradesh Revenue "
            "Code, 2006 (U.P. Act No. 22 of 2006), the Governor is pleased to make the "
            "following amendments to the Uttar Pradesh Land Revenue Rules, 2016:",
            "",
            "1. In Rule 45, for sub-rule (2), the following shall be substituted:",
            "   '(2) The circle rate for agricultural land shall be revised annually based on "
            "   the average market transaction value of the preceding three financial years, "
            "   subject to a maximum increase of 15% per annum.'",
            "",
            "2. After Rule 67, the following new rule shall be inserted:",
            "   'Rule 67A – Digital Land Records: All mutation entries shall be processed "
            "   through the Bhulekh portal within 21 working days of application. Failure to "
            "   process within the stipulated time shall attract a penalty on the concerned "
            "   Lekhpal as prescribed.'",
            "",
            "3. Revenue courts shall adopt video conferencing for proceedings involving "
            "   parties residing beyond 50 km from the court.",
            "",
            "This notification shall come into force from April 1, 2025.",
            "",
            "By Order of the Governor,",
            "Principal Secretary, Revenue Department",
        ],
    },
    # ── Hindi – Uttar Pradesh ───────────────────────────────────────────────
    {
        "folder": "UP",
        "filename": "UP_Budget_Speech_2025_HI.pdf",
        "language": "hi",
        "title": "उत्तर प्रदेश विधान सभा - बजट भाषण 2025-26",
        "category": "DEBATE_TRANSCRIPT",
        "security": "PUBLIC",
        "unicode": True,
        "content": [
            "उत्तर प्रदेश विधान सभा",
            "बजट भाषण 2025-26",
            "दिनांक: 15 मार्च 2025",
            "",
            "माननीय अध्यक्ष महोदय,",
            "",
            "मैं उत्तर प्रदेश के लिए वर्ष 2025-26 का बजट प्रस्तुत करता हूँ।",
            "",
            "कुल बजट अनुमान: रू. 7,36,437 करोड़",
            "राजस्व प्राप्तियाँ: रू. 5,89,150 करोड़",
            "पूंजीगत व्यय: रू. 1,47,287 करोड़",
            "",
            "प्रमुख आवंटन:",
            "",
            "1. शिक्षा विभाग - रू. 89,500 करोड़",
            "   - 10,000 नये प्राथमिक विद्यालय",
            "   - हर ब्लॉक में स्मार्ट स्कूल",
            "   - 50,000 अध्यापकों की नियुक्ति",
            "",
            "2. स्वास्थ्य विभाग - रू. 45,200 करोड़",
            "   - 15 नये मेडिकल कॉलेज",
            "   - हर जिले में 100 बेड का अस्पताल",
            "   - मुफ्त दवाई योजना का विस्तार",
            "",
            "3. कृषि एवं किसान कल्याण - रू. 52,000 करोड़",
            "   - किसान सम्मान निधि: रू. 8,000 प्रत्येक किसान",
            "   - सिंचाई परियोजनाओं का त्वरित निर्माण",
            "   - फसलों का न्यूनतम समर्थन मूल्य में वृद्धि",
            "",
            "4. सड़क एवं परिवहन - रू. 38,000 करोड़",
            "   - लखनऊ-आगरा एक्सप्रेसवे विस्तार",
            "   - 5,000 किमी ग्रामीण सड़कों का निर्माण",
            "",
            "5. महिला सशक्तिकरण - रू. 12,500 करोड़",
            "   - कन्या सुमंगला योजना का विस्तार",
            "   - महिला स्वयं सहायता समूहों को रू. 5 लाख तक का रियायती ऋण",
            "",
            "यह बजट उत्तर प्रदेश को विकास की नई ऊँचाइयों पर ले जाएगा।",
            "धन्यवाद।",
        ],
    },
    {
        "folder": "UP",
        "filename": "UP_Gazette_Education_HI.pdf",
        "language": "hi",
        "title": "उत्तर प्रदेश राजपत्र - शिक्षा विभाग अधिसूचना",
        "category": "GAZETTE_NOTIFICATION",
        "security": "PUBLIC",
        "unicode": True,
        "content": [
            "उत्तर प्रदेश राजपत्र",
            "असाधारण",
            "भाग 4 - खण्ड (क)",
            "प्राधिकार से प्रकाशित",
            "संख्या 891/VII-शि-1-2025 | लखनऊ, दिनांक 5 मार्च 2025",
            "",
            "शिक्षा विभाग",
            "अधिसूचना",
            "",
            "उत्तर प्रदेश शिक्षा संहिता, 2020 की धारा 45 द्वारा प्रदत्त",
            "शक्तियों का प्रयोग करते हुए, राज्यपाल निम्नलिखित संशोधन",
            "करने हेतु प्रसन्न हैं:",
            "",
            "1. नियम 12 में, उपनियम (3) के स्थान पर निम्नलिखित रखा जाएगा:",
            "   '(3) प्रत्येक प्राथमिक विद्यालय में न्यूनतम शिक्षक-छात्र",
            "   अनुपात 1:30 बनाए रखा जाएगा। इस अनुपात से अधिक होने पर",
            "   अतिरिक्त शिक्षकों की नियुक्ति अनिवार्य होगी।'",
            "",
            "2. नियम 28 के पश्चात, निम्नलिखित नया नियम जोड़ा जाएगा:",
            "   'नियम 28-क - डिजिटल शिक्षा: प्रत्येक उच्च प्राथमिक विद्यालय",
            "   में कम से कम एक स्मार्ट क्लासरूम की स्थापना 2026 तक",
            "   अनिवार्य होगी।'",
            "",
            "यह अधिसूचना 1 अप्रैल 2025 से प्रभावी होगी।",
            "",
            "राज्यपाल के आदेश से,",
            "प्रमुख सचिव, शिक्षा विभाग",
        ],
    },
    # ── Confidential – Speaker Only ─────────────────────────────────────────
    {
        "folder": "AP",
        "filename": "AP_Confidential_Privileges_Report_EN.pdf",
        "language": "en",
        "title": "AP Committee of Privileges – Confidential Report",
        "category": "COMMITTEE_REPORT",
        "security": "CONFIDENTIAL",
        "content": [
            "ANDHRA PRADESH LEGISLATIVE ASSEMBLY",
            "COMMITTEE OF PRIVILEGES",
            "STRICTLY CONFIDENTIAL",
            "Report No. CP-12/2025",
            "",
            "Subject: Breach of Privilege by unauthorized disclosure of proceedings of the "
            "Standing Committee on Finance to media outlets.",
            "",
            "1. BACKGROUND",
            "On 28th February 2025, details of the in-camera proceedings of the Standing "
            "Committee on Finance, held on 25th February 2025, were published in two daily "
            "newspapers and three online portals before the report was formally presented "
            "to the House.",
            "",
            "2. INVESTIGATION FINDINGS",
            "2.1 Digital forensic analysis of committee document access logs identified three "
            "accounts that accessed the draft report between 25th and 27th February.",
            "2.2 Two mobile devices were found to contain photographs of the committee "
            "proceedings room during the session.",
            "2.3 Email analysis revealed forwarding of summary documents to external addresses.",
            "",
            "3. PERSONS EXAMINED",
            "The committee examined 8 individuals including committee staff, IT personnel, "
            "and legislative assistants under oath.",
            "",
            "4. RECOMMENDATIONS",
            "4.1 The committee recommends that the House take note of the prima facie "
            "breach of privilege.",
            "4.2 Two individuals be referred to the Ethics Committee for further action.",
            "4.3 Implementation of enhanced document security protocols including watermarked "
            "copies with unique identifiers for each recipient.",
            "4.4 Mobile devices to be deposited before entering committee rooms.",
            "",
            "This report is classified CONFIDENTIAL under Rule 275 of the Rules of "
            "Procedure. Distribution is restricted to the Hon'ble Speaker and members of "
            "the Committee of Privileges.",
        ],
    },
    {
        "folder": "UP",
        "filename": "UP_Committee_Report_Education_EN.pdf",
        "language": "en",
        "title": "Committee Report on Education – UP",
        "category": "COMMITTEE_REPORT",
        "security": "RESTRICTED",
        "content": [
            "UTTAR PRADESH LEGISLATIVE ASSEMBLY",
            "STANDING COMMITTEE ON EDUCATION",
            "Report No. 31 / 2025",
            "RESTRICTED - FOR COMMITTEE MEMBERS AND AUTHORIZED PERSONNEL ONLY",
            "",
            "Subject: Review of Basic and Secondary Education Infrastructure in Uttar Pradesh",
            "",
            "1. INTRODUCTION",
            "This committee was constituted under Rule 268 of the Rules of Procedure of the "
            "Uttar Pradesh Legislative Assembly to examine the state of school infrastructure, "
            "teacher vacancies, and learning outcomes across the State.",
            "",
            "2. KEY FINDINGS",
            "2.1 Basic Education (Classes 1-8):",
            "   - Operational schools: 1,32,450",
            "   - Teacher vacancies: 51,200 (against sanctioned 4,80,000)",
            "   - Schools without functional toilets: 8.4%",
            "",
            "2.2 Secondary Education (Classes 9-12):",
            "   - Operational schools: 27,900",
            "   - Average pupil-teacher ratio: 39:1 (norm: 30:1)",
            "   - Schools with science laboratories: 61%",
            "",
            "2.3 Mid-Day Meal Scheme:",
            "   - Daily beneficiaries: 1.78 Crore students",
            "   - Districts reporting supply irregularities: 11",
            "",
            "3. COMMITTEE OBSERVATIONS",
            "The committee observes that persistent teacher vacancies and infrastructure "
            "gaps in eastern UP districts (Purvanchal) require urgent intervention. Digital "
            "learning adoption remains below 35% in rural blocks.",
            "",
            "4. RECOMMENDATIONS",
            "4.1 Time-bound recruitment to fill 51,200 teacher vacancies by FY 2025-26",
            "4.2 Priority allocation for toilet and drinking-water facilities in deficit schools",
            "4.3 Establish 500 model composite schools across aspirational districts",
            "4.4 Strengthen mid-day meal monitoring through monthly social audits",
            "",
            "This report is classified RESTRICTED under Rule 270 of the Rules of Procedure. "
            "Distribution is limited to the Hon'ble Speaker and Members of the Legislative "
            "Assembly.",
        ],
    },
    {
        "folder": "UP",
        "filename": "UP_Confidential_Security_Assessment_EN.pdf",
        "language": "en",
        "title": "UP Assembly Security Assessment – Confidential",
        "category": "COMMITTEE_REPORT",
        "security": "CONFIDENTIAL",
        "content": [
            "UTTAR PRADESH VIDHAN SABHA",
            "SECURITY AND PROTOCOL ASSESSMENT",
            "STRICTLY CONFIDENTIAL – SPEAKER'S OFFICE ONLY",
            "Reference: SPK/SEC/2025/034",
            "",
            "Subject: Comprehensive Security Review of Legislative Assembly Complex",
            "",
            "1. CURRENT SECURITY INFRASTRUCTURE",
            "1.1 CCTV Coverage: 847 cameras across the complex, 23 non-functional",
            "1.2 Access Control: Biometric entry at 12 of 18 entry points",
            "1.3 Personnel: 340 security staff in 3 shifts",
            "",
            "2. VULNERABILITIES IDENTIFIED",
            "2.1 Service entrance on North Wing lacks biometric verification",
            "2.2 Underground parking area has 4 blind spots in camera coverage",
            "2.3 VIP gallery access protocol allows unvetted visitors with MLA escort",
            "2.4 Emergency evacuation routes 3 and 5 partially obstructed by stored materials",
            "",
            "3. CYBER SECURITY",
            "3.1 Assembly Wi-Fi network penetration test: 2 of 6 access points vulnerable",
            "3.2 Document management system running outdated version with known CVEs",
            "3.3 12 workstations without endpoint protection",
            "",
            "4. RECOMMENDED ACTIONS (Priority Order)",
            "4.1 IMMEDIATE: Repair 23 non-functional CCTV cameras (Est: Rs. 15 Lakh)",
            "4.2 IMMEDIATE: Install biometric at remaining 6 entry points (Est: Rs. 45 Lakh)",
            "4.3 HIGH: Clear evacuation routes and conduct mock drill",
            "4.4 HIGH: Update document management system and patch all workstations",
            "4.5 MEDIUM: Revise VIP gallery access protocol with mandatory pre-registration",
            "",
            "This document is classified under Speaker's discretion. Unauthorized "
            "reproduction or distribution is a breach of privilege.",
        ],
    },
]


# ── PDF Generation ──────────────────────────────────────────────────────────

ARIAL_UNICODE_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


class LegislativePDF(FPDF):
    def __init__(self, use_unicode: bool = False):
        super().__init__()
        self._use_unicode = use_unicode
        if use_unicode and Path(ARIAL_UNICODE_PATH).exists():
            self.add_font("ArialUni", "", ARIAL_UNICODE_PATH, uni=True)

    def _set(self, style: str = "", size: int = 11):
        if self._use_unicode:
            self.set_font("ArialUni", "", size)
        else:
            self.set_font("Helvetica", style, size)

    def header(self):
        self._set("B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Assembly-KB Sample Document", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self._set("", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def _sanitize(text: str) -> str:
    """Replace Unicode characters that Helvetica (Latin-1) cannot render."""
    replacements = {
        "–": "-", "—": "--", "‘": "'", "’": "'",
        "“": '"', "”": '"', "…": "...", " ": " ",
        "₹": "Rs.", "•": "-",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_pdf(doc: dict) -> Path:
    folder = OUTPUT_DIR / doc["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    filepath = folder / doc["filename"]

    use_unicode = doc.get("unicode", False)
    pdf = LegislativePDF(use_unicode=use_unicode)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title
    pdf._set("B", 16)
    pdf.set_text_color(0, 51, 102)
    title = doc["title"] if use_unicode else _sanitize(doc["title"])
    pdf.multi_cell(0, 8, title, align="C")
    pdf.ln(3)

    # Metadata bar
    pdf._set("", 9)
    pdf.set_text_color(80, 80, 80)
    meta_line = (
        f"Language: {doc['language'].upper()}  |  "
        f"Category: {doc['category']}  |  "
        f"Security: {doc['security']}  |  "
        f"State: {doc['folder']}"
    )
    pdf.cell(0, 5, meta_line, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(8)

    # Body
    pdf._set("", 11)
    pdf.set_text_color(0, 0, 0)
    for raw_line in doc["content"]:
        line = raw_line if use_unicode else _sanitize(raw_line)
        if not line.strip():
            pdf.ln(4)
        elif not use_unicode and (line.isupper() or line.startswith("CHAPTER")):
            pdf._set("B", 12)
            pdf.set_text_color(0, 51, 102)
            pdf.multi_cell(0, 6, line)
            pdf._set("", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)
        elif raw_line.startswith("   "):
            pdf.set_x(20)
            pdf.multi_cell(0, 5, line.strip())
        else:
            pdf.multi_cell(0, 5, line)
        pdf.ln(1)

    pdf.output(str(filepath))
    return filepath


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating {len(DOCUMENTS)} sample documents in {OUTPUT_DIR}\n")

    for doc in DOCUMENTS:
        path = generate_pdf(doc)
        sec_badge = {"PUBLIC": " ", "RESTRICTED": " [R]", "CONFIDENTIAL": "[C]"}
        print(f"  {sec_badge.get(doc['security'], '')}  {doc['folder']}/{doc['filename']}")

    print(f"\nDone. {len(DOCUMENTS)} PDFs created.")
    print("\nBreakdown:")
    by_state = {}
    by_sec = {}
    by_lang = {}
    for d in DOCUMENTS:
        by_state[d["folder"]] = by_state.get(d["folder"], 0) + 1
        by_sec[d["security"]] = by_sec.get(d["security"], 0) + 1
        by_lang[d["language"]] = by_lang.get(d["language"], 0) + 1
    print(f"  States:    {by_state}")
    print(f"  Security:  {by_sec}")
    print(f"  Languages: {by_lang}")


if __name__ == "__main__":
    main()
