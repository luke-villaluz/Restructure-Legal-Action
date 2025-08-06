ANALYSIS_PROMPT = """

AI Contract Review Prompt – Corporate Restructure Notification Assessment

It is important to note that, anytime a corporation restructures or changes their name, a contract or agreement is considered to be assigned or reassigned
With regards to these contracts and agreements,  Xponance will often be referred to as a Manager, or Investment Manager .
You are reviewing a contract or agreement to determine if a change in the firm's legal name (from "Xponance Inc." to "Xponance LLC") or a Corporate Restructuring to an LLC from being Incorporated requires prior notification or consent from the counterparty or client.

CONTRACT TEXT:
{contract_text}

SEARCH TERMS TO FOCUS ON:
{search_terms}

Return EXACTLY ONE JSON object with these fields:
{{

    "contract_name": "Name of the contract",
    "effective_date": "Effective date of the contract",
    "renewal_termination_date": "Renewal or termination date",
    "assignment_clause_reference": "Assignment clause reference if applicable, otherwise 'N/A'",
    "notices_clause_present": "Yes/No/Not Specified - If yes, provide referennce and cite it",
    "action_required": "Specific action or noticerequired prior to assignment of contract or agreement, name change or corporate restructure. If no action is required, return 'No Action Required'. DO NOT GIVE ANY RECOMMENDATIONS, THIS IS SOLELY IF SOMETHING IS REQUIRED PER CONTRACT OR AGREEMENT",
    "recommended_action": "Recommended next steps, please include a time range for notification only if stated explicitly in the contract, as well as if an acknowledgement or delivery confirmation is required by the client (often mentioned in the notices clause)"
}}

**IMPORTANT: Analyze all documents as ONE contract package and return exactly ONE summary object, not one object per document file.**
Please populate all fields to the best of your ability using the contract content, and flag any uncertainties clearly. Output should be valid JSON.

"""