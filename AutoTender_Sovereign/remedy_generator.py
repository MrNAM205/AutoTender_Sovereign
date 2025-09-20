import argparse
import datetime

REMEDY_TEMPLATES = {
    "dishonor_of_tender": """
# AFFIDAVIT OF NON-RESPONSE / DISHONOR OF TENDER

**Date:** {date}
**To:** [Creditor Name]
**From:** [Your Name]
**Account:** [Account Number]

This affidavit is to certify that a lawful tender of payment was dispatched to you on [Date of Tender] via certified mail #[Tracking Number].

As of this date, no response has been received, and the tender is presumed to have been dishonored.

Per UCC § 3-502, this constitutes a formal dishonor of the instrument.

I hereby demand that the debt associated with the above-mentioned account be discharged in full, as per UCC § 3-603(b).

Failure to provide evidence of discharge within 15 days will result in the issuance of IRS Form 1099-C for cancellation of debt.

---
/s/ [Your Name]
""",
    "denial_of_negotiability": """
# NOTICE OF DISPUTE: Unlawful Denial of Negotiable Instrument

**Date:** {date}
**To:** [Creditor Name]
**From:** [Your Name]
**Account:** [Account Number]

This notice is in response to your claim, stated on the remittance document, that it is "not a negotiable instrument".

This claim is in direct contradiction to the definition of a negotiable instrument as laid out in UCC § 3-104. The remittance coupon, when endorsed and tendered for payment, meets all the requirements of a negotiable instrument.

Your unilateral declaration does not supersede the Uniform Commercial Code.

Please be advised that your refusal to accept this lawful tender constitutes a dishonor of the instrument under UCC § 3-502.

I demand that you process the tender as presented. Failure to do so will be considered a formal dishonor and will be escalated accordingly.

---
/s/ [Your Name]
""",
    "tender_letter": """
# TENDER OF PAYMENT LETTER

**Date:** {date}
**To:** {creditor_name}
    {creditor_address}
**From:** {user_name}
    {user_address}

**SUBJECT:** Private Administrative Process - Tender of Payment for Instrument {bill_file_name}

Dear Sir/Madam,

This correspondence serves as a formal tender of payment, presented in good faith, for the instrument identified as "{bill_file_name}". This instrument, having been properly endorsed and accepted for value, is hereby presented as a valid and lawful tender for the discharge and settlement of any alleged obligation or account associated therewith.

Be advised that this tender is made in accordance with the principles of commercial law and equity. Under Uniform Commercial Code (UCC) 3-603, a tender of payment of an obligation to pay an instrument made to a person entitled to enforce the instrument, if refused, discharges the obligation of the obligor to pay interest on the obligation after the due date and discharges any party with a right of recourse against the obligor to the extent of the amount of the tender.

Your refusal to accept this lawful tender of payment will be considered a dishonor of a commercial instrument and a refusal of a valid tender. All rights, remedies, and recourse, both at law and in equity, are expressly reserved without prejudice, pursuant to UCC 1-308.

This is a private administrative process. Your acceptance of this tender, or your failure to return the instrument with specific objections within [e.g., 3, 7, 10] days, will be deemed as acceptance of this tender and agreement to the discharge of the obligation.

Sincerely,

By: {user_name}
Authorized Representative / Agent
All Rights Reserved. Without Prejudice. UCC 1-308.
"""
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a remedy document based on a specific violation.")
    parser.add_argument("--violation", required=True, choices=REMEDY_TEMPLATES.keys(), help="The type of violation to generate a remedy for.")
    parser.add_argument("--output", help="Path to save the remedy document. Defaults to [violation]_remedy.md")
    # New arguments for the tender letter
    parser.add_argument("--user-name", help="Your name (for tender letter).")
    parser.add_argument("--user-address", help="Your address (for tender letter).")
    parser.add_argument("--creditor-name", help="Creditor's name (for tender letter).")
    parser.add_argument("--creditor-address", help="Creditor's address (for tender letter).")
    parser.add_argument("--bill-file-name", help="The name of the bill file (for tender letter).")

    args = parser.parse_args()

    output_path = args.output if args.output else f"{args.violation}_remedy.md"
    
    template = REMEDY_TEMPLATES.get(args.violation)
    if template:
        try:
            if args.violation == "tender_letter":
                if not all([args.user_name, args.user_address, args.creditor_name, args.creditor_address, args.bill_file_name]):
                    raise ValueError("Missing required arguments for tender letter. Please provide all --user-*, --creditor-*, and --bill-file-name arguments.")
                content = template.format(
                    date=datetime.date.today().strftime("%Y-%m-%d"),
                    user_name=args.user_name,
                    user_address=args.user_address,
                    creditor_name=args.creditor_name,
                    creditor_address=args.creditor_address,
                    bill_file_name=args.bill_file_name
                )
            else:
                content = template.format(date=datetime.date.today().strftime("%Y-%m-%d"))
            
            with open(output_path, "w") as f:
                f.write(content)
            print(f"Successfully generated remedy document at {output_path}")
        except (ValueError, KeyError) as e:
            print(f"Error generating document: {e}")
    else:
        print(f"Error: No template found for violation '{args.violation}'")