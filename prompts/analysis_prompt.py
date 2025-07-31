ANALYSIS_PROMPT = """
AI Contract Review Prompt – Corporate Restructure Notification Assessment

AI Contract Review Prompt – Corporate Restructure Notification Assessment

You are reviewing a contract to determine if a change in our company’s legal name (e.g., from "Xponance Inc." to "Xponance LLC") or a Corporate Restructuring to an LLC from being Incorporated requires prior notification or consent from the counterparty. Please analyze the contract and return your findings in the following structured tabular format.

CONTRACT TEXT:
{contract_text}

SEARCH TERMS TO FOCUS ON:
{search_terms}

You will be returning a JSON object with the following fields, for each field is there possible option if they have one.

Contract Name
Contract Counterparty
Effective Date
Renewal/Termination Date
Corporate Restructure or Name Chane Requires Notification or Consent? Valid responses: Yes / No / Not Specified
Clause Reference (if Yes) Provide section number and brief excerpt or title of clause
Is a Corporate Restructure or a Name Change Considered an Assignment? Valid responses: Yes / No / Unclear
Assignment Clause Reference (if Yes) Provide section number and relevant language
Material Corporate Structure Change or Name Change Clauses?
Does the contract require notification for changes to corporate status? Yes / No
Notices Clause Present? Yes / No, and specify if it mentions name or structural changes
Action Required Prior to Name Chane or Corporate Restructure Valid responses: Notification Required / Consent Required / No Action Required / Further Legal Review Recommended
Recommended Action Options: Send Notification / Request Consent / No Action / Escalate for Legal Review

Return EXACTLY ONE JSON object with these fields:
{{
    "contract_name": "Name of the contract",
    "contract_counterparty": "Name of the counterparty",
    "effective_date": "Effective date of the contract",
    "renewal_termination_date": "Renewal or termination date",
    "name_change_requires_notification": "Yes/No/Not Specified - whether corporate restructure or name change requires notification or consent",
    "clause_reference": "Specific clause reference if notification/consent is required, otherwise 'N/A'",
    "is_assignment": "Yes/No/Unclear - whether corporate restructure or name change is considered an assignment",
    "assignment_clause_reference": "Assignment clause reference if applicable, otherwise 'N/A'",
    "material_corporate_structure_clauses": "Yes/No/Not Specified - whether there are material corporate structure change or name change clauses",
    "notices_clause_present": "Yes/No/Not Specified - whether a notices clause is present",
    "action_required": "Specific action required prior to name change or corporate restructure",
    "recommended_action": "Recommended next steps"
}}

**IMPORTANT: Analyze all documents as ONE contract package and return exactly ONE summary object, not one object per document file.**

Please populate all fields to the best of your ability using the contract content, and flag any uncertainties clearly. Output should be valid JSON.
"""