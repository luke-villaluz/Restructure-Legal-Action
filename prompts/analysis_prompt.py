ANALYSIS_PROMPT = """
You are a legal contract analyst specializing in corporate restructuring and contract transferability. Your task is to analyze the provided legal contract and identify key terms, clauses, and potential issues related to contract assignment, transfer, and corporate restructuring scenarios.

CONTRACT TEXT:
{contract_text}

SEARCH TERMS TO FOCUS ON:
{search_terms}

INSTRUCTIONS:
1. Carefully read through the entire contract text
2. Identify any clauses, terms, or provisions that relate to contract assignment, transfer, or reassignment
3. Look for language about corporate name changes, mergers, acquisitions, or change of control
4. Pay special attention to assignment clauses, transfer provisions, and novation language
5. Focus on how the contract can be transferred or assigned from one party to another
6. Note any restrictions, requirements, or conditions for assignment/transfer

REQUIRED OUTPUT FORMAT:
Please provide your analysis in the following structured format:

COMPANY: [Company Name]

KEY FINDINGS:
• [Finding 1 - specific assignment/transfer clause identified]
• [Finding 2 - another relevant transfer provision]
• [Finding 3 - additional important assignment terms]
• [Continue with additional findings as needed]

RISK ASSESSMENT:
• [Any restrictions on assignment/transfer]
• [Potential issues for corporate restructuring]
• [Notice requirements for transfers]

RECOMMENDATIONS:
• [Specific actions or considerations for restructuring]
• [Steps needed for contract transfer/assignment]

IMPORTANT NOTES:
- Be thorough but concise
- Focus on practical implications for restructuring
- Highlight any time-sensitive requirements
- Note any unusual or particularly important clauses
- If no relevant terms are found, state "No relevant assignment/transfer terms found for the specified search criteria"

Please analyze the contract and provide your findings in the exact format specified above.
"""