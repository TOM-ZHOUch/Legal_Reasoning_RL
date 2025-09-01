

SYSTEM_PROMPT: str= """
"""

USER_PROMPT: str= """ 
Please reason step by step, and put your final answer within \boxed{{}}.
Question: {question}
<think>
"""




JUDGE_SYSTEM_PROMPT: str = """
You are a precise answer validator. Your task is to determine if a student's answer is equivalent to the ground truth answer.

Guidelines:
1. Do not solve the problem - only compare the given answers
2. Check for mathematical equivalence, not just exact string matches
3. Consider different valid formats (e.g., 1/2 = 0.5 = 50%)
4. Ignore minor formatting differences (spaces, capitalization)
5. For algebraic expressions, check if they reduce to the same result

Output Format:
- If answers are equivalent: 
[[FINAL DECISION]] Yes
- If answers are not equivalent:
[[FINAL DECISION]] No
- No additional explanation or commentary needed
"""

JUDGE_USER_PROMPT: str= """ 
[[QUESTION]]
{question}
[[GROUND TRUTH]]
{ground_truth}
[[STUDENT ANSWER]]
{student_answer}
"""



# COMPRESS_COT_SYSTEM_PROMPT: str = """
# You are a logic expert specializing in refining complex reasoning chains to remove redudent expressions while preserving logical validity. Your task is to:

# 1. Maintain the overal logic structure
# 2. Eliminate redundant or repetitive statements (e.g., "Okay, so the question is...")
# 3. Remove thinking-aloud elements (e.g., "Wait, maybe this is an application of..."), retaining only the final correct reasoning process
# 4. Preserve all critical intermediate conclusions
# 5. Use precise, unambiguous language
# 6. Ensure the text is readable.

# Output the compressed reasoning in this format:
# [[REFINED REASONING]]
# """

# COMPRESS_COT_USER_PROMPT: str = """
# [[ORIGINAL QUESTION]]
# {question}

# [[ORIGINAL REASONING]]
# {reasoning}

# Please compress the above reasoning while preserving logical validity.
# """


COMPRESS_COT_SYSTEM_PROMPT: str = """
You are a logic expert specializing in distilling complex reasoning chains into concise, rigorous arguments. Your task is to compress reasoning while preserving logical validity by:

1. Maintaining the complete logical structure and flow of the original argument
2. Eliminating redundancies, filler phrases, and meta-commentary (e.g., "Let me think about this...", "The question asks...")
3. Removing exploratory paths and false starts, retaining only the correct reasoning process
4. Preserving all essential intermediate steps and conclusions
5. Using precise mathematical and logical notation where appropriate
6. Ensuring the compressed reasoning remains clear and readable for a technical audience

The compressed reasoning should be a streamlined version of the original that a mathematician or logician would recognize as logically equivalent.

Output the compressed reasoning in this format:
[[COMPRESSED REASONING]]
"""

COMPRESS_COT_USER_PROMPT: str = """
[[ORIGINAL QUESTION]]
{question}

[[ORIGINAL REASONING]]
{reasoning}

Compress this reasoning into a concise, logically equivalent form that preserves all essential steps and conclusions.
"""

############################ logic extraction v1
EXTRACT_LOGIC_SYSTEM_PROMPT: str = """
You are an expert in logic reasoning and conflict resolution strategies. Your task is to analyze the provided question and reasoning process to extract:
1. Facts stated in the question
2. Logic modules - connected groups of original sentences that form complete logical reasoning chains

Guidelines:
1. You can extract necessary facts from the question and from you commonsense knowledge. The facts should be helpful for the reasoning process.
2. When identifying logic modules, preserve the exact original sentences
3. Each module should be a continuous text block containing 2+ logically connected sentences
4. Keep the original flow and connections between sentences intact
5. Do not separate or break up connected reasoning

Output Format:
Facts:
- List each distinct fact from the question
- Format as "Fact 1: [exact statement]"

Logic Modules:
- Each module should be a continuous block of text containing the original connected sentences
- Include only complete logical sequences
- Present as a single paragraph without breaks between sentences

Example Output:
Facts:
fact1: That chipping does not occurs and this gybing does not happens. 
fact2: This ninjutsu does not happens. 
fact3: That that Conservative does not happens and that superconductivity does not occurs is caused by that this blandishing 1900s does not occurs.
fact4: That this gybing does not happens is prevented by this complimenting Chamaeleo. 
fact5: That that chipping occurs is triggered by this bubbling Cheever.

Module1: 
We begin by assuming that the bubbling Cheever occurs.
Given that the bubbling Cheever’s occurrence would trigger chipping, this assumption implies chipping must take place.
However, we already know independently that chipping does not occur.
These two conclusions clash, so our initial assumption must be wrong; hence the bubbling Cheever does not happen.

Module 2:
[Next continuous block of logically connected sentences]

"""

EXTRACT_LOGIC_USER_PROMPT: str = """
Please analyze the following:
Question: {question}
Reasoning: {reasoning}

Extract the facts and logic modules, keeping connected sentences together in continuous blocks.
"""
############################

# ########### fact conversion
# FACTS_SYSTEM_PROMPT: str= """
# You are an expert in converting natural language facts into first-order logic (FOL) statements using Z3. 
# Your task is to formalize a set of facts into Z3 Python code.

# Write the beginning part of a Python program that formalizes these facts using Z3.
# Include all necessary variable declarations, constants, and assertions that represent the facts.
# Do not include any proof or solver code yet - just the formalization of the facts.

# Output Format:
# ```python
# from z3 import *
# # Your formalization of the facts here
# # Include all necessary declarations and assertions
# ```
# """

# FACTS_USER_PROMPT: str= """
# Please formalize the following facts into Z3 Python code:

# Facts:
# {facts}

# Provide only the formalization of these facts. The reasoning modules will be added later.
# """


# ========================== 3. NL→FOL ==========================
NL2FOL_SYSTEM_PROMPT: str = """
You are an expert in converting natural language reasoning into first-order logic (FOL) statements in the {domain} domain. Your task is to analyze facts and reasoning processes and present them using first-order logic and express in python. 

Write a complete python code and present the FOL reasoning by using the 'from z3 import *'

You can either prove the hypothesis or disprove it, depending on the facts and reasoning provided.

Output Format:
Python Code:
```python
from z3 import *
# Your complete z3 code here
```
Status:
proved or disproved

"""

NL2FOL_USER_PROMPT: str = """
Please analyze the following:
Facts: {facts}
Reasoning: {reasoning}
"""

#===========================

NL2FOL_WITH_ERROR_SYSTEM_PROMPT: str = """
You are an expert in converting natural language reasoning into first-order logic (FOL) statements. Your task is to analyze facts and reasoning processes and present them in z3 format in python. 

Write a complete python code and present the FOL reasoning by using the 'from z3 import *'
You can either prove the hypothesis or disprove it, depending on the facts and reasoning provided.

You are also given an incorrect proof formula, you need to correct it and provide the correct z3 code.

Output Format:
Z3 Python Code:
```python
from z3 import *
# Your complete z3 code here
```
Status:
proved or disproved

"""

NL2FOL_WITH_ERROR_USER_PROMPT: str = """
Please analyze the following:
Facts: {facts}
Reasoning: {reasoning}
Incorrect Proof Formula: {incorrect_proof_formula}
Error Message: {error_message}
Please correct the proof formula and provide the correct z3 code.
"""


## summary for final answer

SUMMARY_SYSTEM_PROMPT: str = """
You are an expert at explaining complex logical reasoning in simple terms. Your task is to:

1. Take a question, its detailed reasoning process (which may contain formal notation), and the correct answer
2. Transform the reasoning into clear, everyday language that anyone can understand
3. Break down complex steps into digestible pieces
4. Present the summary in a conversational, engaging way
5. Only summarize the provided reasoning - do not attempt to solve the problem independently.
6. Conclude with the final answer formatted within \\box{{}}

Remember to:
- Avoid technical jargon and formal notation in your explanation
- Use simple analogies when helpful
- Keep the explanation concise yet complete
- Maintain a logical flow from start to finish

Output format:
[[SUMMARY]]
"""

SUMMARY_USER_PROMPT: str = """
Please explain this problem's solution:

[[QUESTION]]
{question}

[[STEP-BY-STEP REASONING]]
{reasoning}

[[FINAL ANSWER]]
{answer}
"""