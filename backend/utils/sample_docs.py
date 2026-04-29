"""
Sample banking and insurance documents for demonstration.
These contain realistic (but entirely synthetic) data.
"""

SAMPLE_DOCUMENTS = {
    "wire_transfer": {
        "title": "International Wire Transfer Instruction",
        "type": "wire_transfer",
        "text": """WIRE TRANSFER INSTRUCTION

Date: 15 March 2024
Reference: WT-2024-03-0892

Beneficiary Information:
Name: Dr. Sarah Mitchell
Account Number: 4521890123456789
IBAN: GB29NWBK60161331926819
SWIFT/BIC: NWBKGB2L
Bank: NatWest Bank plc
Address: 15 Finance Street, London EC2V 8RT

Originator:
Name: Apex Capital Holdings Inc.
Account: 9876543210
Routing Number: 021000021
ABA/Transit: 021000021
Tax ID (EIN): 47-1234567

Transfer Details:
Amount: USD 2,500,000.00
Currency: USD
Value Date: 18 March 2024
Purpose: Investment capital transfer per agreement dated 01 Jan 2024

Correspondent Bank:
JPMorgan Chase Bank N.A.
SWIFT: CHASUS33

Authorized by: Mr. James Harrington, Chief Financial Officer
Contact: j.harrington@apexcapital.com | +1-212-555-0187

All transfers are subject to compliance review under AML/KYC regulations.
Policy Reference: POL-COMP-2024-0447
"""
    },
    "insurance_claim": {
        "title": "Insurance Claim Form",
        "type": "insurance_claim",
        "text": """INSURANCE CLAIM SUBMISSION

Claim Number: CLM-2024-089234
Policy Number: POLHLT-2023-447821
Date of Claim: 22 Feb 2024
Date of Incident: 19 Feb 2024

Policyholder Information:
Name: Mrs. Priya Sharma
SSN: 456-78-9012
PAN: BKQPS8832P
Date of Birth: 14 Jul 1982
Phone: +91-98765-43210
Email: priya.sharma@gmail.com
Address: 42 Palm Grove, Bangalore 560001, Karnataka

Policy Details:
Policy Type: Comprehensive Health Insurance
Coverage Amount: INR ₹5,000,000.00
Deductible: INR ₹25,000.00
Premium: INR ₹85,000 per annum
Insurer: LifeShield Insurance Corporation Ltd.

Claim Description:
Hospitalization from 19 Feb 2024 to 21 Feb 2024
Hospital: Apollo Hospitals Group
Treating Physician: Dr. Rajesh Kumar
Diagnosis: Acute appendicitis requiring emergency surgery
Claimed Amount: INR ₹320,500.00

Bank Details for Settlement:
Account Holder: Mrs. Priya Sharma
Account Number: 91234567890
IFSC: HDFC0001234
Bank: HDFC Bank Ltd.

Supporting Documents Reference: DOC-2024-CLM-089234-A through DOC-2024-CLM-089234-F

Adjuster: Ms. Karen Weiss
Adjuster ID: ADJ-4521
Contact: k.weiss@lifeshield.com
Approved Date: 28 Feb 2024
Settlement Amount: INR ₹298,750.00
"""
    },
    "loan_agreement": {
        "title": "Mortgage Loan Agreement",
        "type": "loan",
        "text": """MORTGAGE LOAN AGREEMENT

Loan ID: LN-2024-087654
Date: 01 April 2024

BORROWER INFORMATION
Full Name: Mr. Robert Chen
SSN: 123-45-6789
Date of Birth: 03 Nov 1978
Phone: (555) 234-5678
Email: robert.chen@email.com

CO-BORROWER
Full Name: Mrs. Linda Chen
SSN: 987-65-4320

LENDER
Institution: First National Bank Corporation
EIN: 52-1234567
ABA Routing Number: 026009593
Loan Officer: Ms. Jennifer Brooks
Contact: j.brooks@fnbc.com | (555) 800-1234

LOAN DETAILS
Loan Amount: USD $485,000.00
Interest Rate: 6.875% per annum (fixed)
Term: 360 months (30 years)
Monthly Payment: USD $3,187.42
Origination Date: 01 April 2024
Maturity Date: 01 April 2054
Loan Type: Conventional Fixed Rate Mortgage

PROPERTY
Address: 2847 Maple Drive, Austin TX 78701
Purchase Price: USD $605,000.00
Appraised Value: USD $612,500.00
LTV Ratio: 79.17%

DISBURSEMENT ACCOUNT
Bank: Wells Fargo Bank N.A.
SWIFT: WFBIUS6S
Account Number: 4532109876543
Routing: 121000248

This agreement is governed by Federal Reserve Regulation Z and the Truth in Lending Act.
Reference Policy: POL-MTG-UNDERWRITING-2024-V3.1
"""
    },
    "kyc_doc": {
        "title": "KYC Verification Document",
        "type": "kyc",
        "text": """KNOW YOUR CUSTOMER (KYC) VERIFICATION RECORD

KYC ID: KYC-2024-CC-00912
Status: VERIFIED
Verification Date: 10 Jan 2024

CUSTOMER PROFILE
Full Name: Dr. Mohammed Al-Rashid
Customer ID: CUST-00456789
Date of Birth: 29 Sep 1975
Nationality: UAE
Passport Number: A12345678
Tax ID: 36-9876543
Phone: +971-50-123-4567
Email: m.alrashid@investcorp.ae

ADDRESS VERIFICATION
Residential: Villa 47, Palm Jumeirah, Dubai, UAE 00000
Correspondence: PO Box 12345, DIFC, Dubai, UAE

FINANCIAL PROFILE
Occupation: Chief Investment Officer
Employer: Gulf Meridian Capital Ltd.
Annual Income: USD $1,200,000.00
Source of Funds: Salary, investment returns, real estate

PRIMARY ACCOUNT
Account Number: 7845123698
IBAN: AE070331234567890123456
SWIFT/BIC: NBADAEAA
Bank: National Bank of Abu Dhabi

SECONDARY ACCOUNT (Trading)
Account Number: 9012345678901
IBAN: DE89370400440532013000
Bank: Deutsche Bank AG
SWIFT: DEUTDEDB

COMPLIANCE NOTES
Risk Rating: MEDIUM
PEP Status: No
Sanctions Check: CLEAR — checked against OFAC, EU, UN lists on 10 Jan 2024
Enhanced Due Diligence: Not required
Next Review Date: 10 Jan 2025
Compliance Officer: Mr. David Stern
Reference Policy: POL-COMP-KYC-2024-V2
"""
    }
}


def get_sample(key: str) -> dict:
    return SAMPLE_DOCUMENTS.get(key, SAMPLE_DOCUMENTS["wire_transfer"])


def list_samples() -> list:
    return [
        {"key": k, "title": v["title"], "type": v["type"]}
        for k, v in SAMPLE_DOCUMENTS.items()
    ]
