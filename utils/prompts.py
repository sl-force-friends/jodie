"""
prompts.py
"""
from pydantic import BaseModel, Field

class TitleCheck(BaseModel):
    """
    Class for the title check
    """
    does_title_match: bool = Field(description="Boolean indicator for whether the given job title reasonably fits the given job description")

class AlternativeTitles(BaseModel):
    """
    Class for the alternative titles
    """
    alternative_titles: list[str] = Field(min_items=1, max_items=3, description="List of alternative job titles")

class PositiveContentCheck(BaseModel):
    """
    Class for the positive content check
    """
    employee_value_proposition: bool = Field(description="Binary value indicating if the Employee Value Proposition is present")
    job_summary_and_responsibilities: bool = Field(description="Binary value indicating if the Job Summary and Responsibilities are present")
    required_technical_competencies: bool = Field(description="Binary value indicating if the Required Technical Competencies are present")
    required_behavioural_competencies: bool = Field(description="Binary value indicating if the Required Behavioural Competencies are present")
    preferred_technical_competencies: bool = Field(description="Binary value indicating if the Preferred Technical Competencies are present")
    preferred_behavioural_competencies: bool = Field(description="Binary value indicating if the Preferred Behavioural Competencies are present")
    example_activities: bool = Field(description="Binary value indicating if the Example Activities are present")
    required_certification: bool = Field(description="Binary value indicating if the Required Certification is present")

class NegativeContentCheck(BaseModel):
    """
    Class for the negative content check
    """
    required_years_of_experience: bool = Field(description="Binary value indicating if the requirements of years of experience is present")
    required_formal_education: bool = Field(description="Binary value indicating if the requirements of specific formal education is present")

JD_SUGGESTION_SYSTEM_MESSAGE = """
You are a job re-design consultant in Singapore helping company. increase their productivity and increase talent attraction.
You will receive a job description and extracts from report about the future of work.
These reports outline how jobs will need to evolve in the future, or list the skills that will be in demand.
You shall provide actionable recommendations to improve the JD/job based on the report's extracts.
Do NOT make reference to these extracts given.

Your reply should be no more than 200 words.

Imagine you are speaking directly to the employer posting the job.

Use markdown bold (i.e. **bold**) to highlight the key points.

Begin directly with the recommendation. For example: "You may want to consider <insert action>"
"""

REWRITE_SYSTEM_MESSAGE = """
You are an experter recruiter in Singapore, and your task is to re-write the given job posting into a more appealing one.

Be sucinct and engaging.

Reformat the job posting into the following sections:
- Employee value proposition.
- Job summary
- Job responsibilities.
- Example activities.
- Required technical competencies.
- Required behavioural competencies.
- Preferred technical competencies.
- Preferred behavioural competencies.
- Required certification.

If the original job description is missing any of these sections, DO NOT MAKE CONTENT UP.
Instead, you should include placeholder text for them. For example "[insert certification 1, if relevant]" or "[insert behavioural competencies]".

Think step by step.

Reply in markdown code, but no codeblock.
The sections will be in bold text.
"""
