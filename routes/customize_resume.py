from datetime import datetime
from flask import abort, redirect, render_template, request
from idli import VNN
from pydantic import BaseModel, Field
from pydantic_ai import Agent, TextOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

import config
from db import Job, CustomizedResume, UserResume
from web_utils import wrap
  

METHODS = ['GET', 'POST']

def text_output_fn(x: str):
    return x


def handler(job_id):
    if not request.user:
        return redirect('/')
    
    resume = UserResume.select(id=request.user.id).one()
    if not resume:
        return redirect('/profile?reason=NO_RESUME_FOR_CUSTOMIZE')
    
    job = Job.select(id=job_id).one()
    if not job:
        return "Job Not Found", 404
    
    llm_agent = Agent(
        OpenAIChatModel(
            config.LLM_API_MODEL,
            provider = OpenAIProvider(
                api_key = config.LLM_API_KEY,
                base_url = config.LLM_API_URL,
            )
        ),
        output_type = TextOutput(text_output_fn),
    )
    
    custom_resume = CustomizedResume.select(
        user_id = request.user.id,
        job_id = job.id
    ).one()
    
    if request.method == 'GET':
        if custom_resume:
            return wrap(render_template(
                'custom_resume.html', 
                resume = custom_resume,
                job = job,
            ))
        else:
            return "Custom Resume Not Found", 404
    
    
    if not custom_resume:
        custom_resume = CustomizedResume(
            user_id = request.user.id,
            job_id = job.id,
            created = datetime.now()
        )
    
    prompt = f"""
        Customize the resume given below for the job description given below.
        Use only facts provided in the resume, do not add any new information or assume anything.
        Your job is to only to polish the resume and make it more presentable for the given job description.
        The idea is to rewrite the resume to better highlight the relevant experience for the job description.
        Your output must be in markdown format that will directly be converted into a resume file by the application that is calling you with this prompt via an API.
        Include all the factual information from the original resume.
        Only the sentences, word choice and ordering of sections may change.
        Absoulutely do not use em dashes o any other dashes. 
        Keep the style and language human-like, similar to the original resume, but grammatically correct.
        The input resume may not have clear formatting, but use clear formatting for the output, like #, ##, ### and hyphen for bullet points and so on.
        Format all links to clickable markdown adding 'https://' or 'mailto:' if needed.
        Do not add any non-working links, if some information or link is not there, just omit the link.
        The resume must begin with summary a section explaining how the candidate is suitable for the job description based on known facts from the resume. If there is an existing resume section, tweak it, otherwise draft this section from scratch.
        Do not use any HTML tags in your output at all.
        
        <xerowork-user-resume-markdown>
          {resume.markdown_content}
        </xerowork-user-resume-markdown>
        
        <job-title>{job.title}</job-title>
        <job-hiring-organization>{job.org_name}</job-hiring-organization>
        <job-location>{job.loc_locality}</job-location>
        <job-description>{job.description}</job-description>
    """
    
    llm_result = llm_agent.run_sync(prompt, model_settings = dict(
        max_tokens=8192
    ))
  
    custom_resume.markdown_content = llm_result.output
    custom_resume.updated = datetime.now()
    custom_resume.save()
    
    return redirect(f'/customize-resume/{job.id}')