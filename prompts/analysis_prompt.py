ANALYSIS_PROMPT = """
You are analyzing contracts for name change notification requirements ONLY.

CONTRACT TEXT:
{contract_text}

SEARCH TERMS TO FOCUS ON:
{search_terms}

CRITICAL INSTRUCTIONS:
- Answer ONLY the specific questions below
- Do NOT provide general contract summaries
- Do NOT generate fake contract content
- Focus ONLY on name change and assignment clauses
- Use the EXACT format shown below

REQUIRED OUTPUT FORMAT:
You MUST respond in this exact format with these exact field names:

Name Change Requires Notification?: Yes or No or Not Specified
Is Name Change Considered an Assignment?: Yes or No or Unclear
Assignment Clause Reference (if Yes): Section number and relevant language, or leave blank if No
Does the Contract Require Notification for Changes to Corporate Status?: Yes or No
Notices Clause Present?: Yes or No, and specify if mentions name/structural changes
Action Required Prior to Name Change: Notification Required or Consent Required or No Action Required or Further Legal Review Recommended
Recommended Action: Send Notification or Request Consent or No Action or Escalate for Legal Review

EXAMPLE OF GOOD RESPONSE:
Name Change Requires Notification?: Yes
Is Name Change Considered an Assignment?: Yes
Assignment Clause Reference (if Yes): Section 12.1 - "Neither party may assign this Agreement without prior written consent"
Does the Contract Require Notification for Changes to Corporate Status?: No
Notices Clause Present?: Yes - mentions name changes in Section 15
Action Required Prior to Name Change: Consent Required
Recommended Action: Request Consent

EXAMPLE OF NO RESTRICTIONS:
Name Change Requires Notification?: No
Is Name Change Considered an Assignment?: No
Assignment Clause Reference (if Yes): 
Does the Contract Require Notification for Changes to Corporate Status?: No
Notices Clause Present?: No
Action Required Prior to Name Change: No Action Required
Recommended Action: No Action

CRITICAL: Follow the exact format above. Do not add explanations or summaries.
"""