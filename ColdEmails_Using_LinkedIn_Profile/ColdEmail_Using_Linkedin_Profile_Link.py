import os
from exa_py import Exa
from langchain.agents import tool
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, Task, Crew, Process
import json
from crewai_tools import WebsiteSearchTool
import streamlit as st

load_dotenv()

# Load the google gemini api key
genai.configure(api_key="GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    # Set gemini pro as llm
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.5)

#tool = JSONSearchTool(json_path='C:/Users/Admin/Desktop/data.json')

# Restricting search to a specific JSON file
# Loading the json file into the function

from textwrap import dedent # type: ignore
from crewai import Agent

      
class OutreachAgents():
	def research_agent(self):
		return Agent(
			role='Research Specialist',
			goal='Become an expert in analyzing social media data to extract valuable information for personalized outreach.',
			tools=[WebsiteSearchTool(website='Linkedin Profile Link')],
			backstory=dedent("""\
					A data detective with a knack for uncovering hidden gems in social media data. Your mission is
               to use your skills to understand the prospect's interests, challenges, and industry engagement to craft the perfect outreach strategy.
               Use techniques like keyword matching and sentiment analysis to achieve this.
					"""),
			verbose=True,
			llm=llm, max_iter=5
		)
   

	def email_specialist(self):
		return Agent(
			role='Email Specialist',
			goal='Master the art of crafting high-converting cold emails that grab attention and lead to successful connections.',
			tools=[WebsiteSearchTool(website='Linkedin Profile Link')],
			backstory=dedent("""\
					A seasoned email copywriter with a keen understanding of human psychology. 
               Your expertise lies in crafting persuasive messages that resonate with the recipient and drive action."""),
			verbose=True,
			llm=llm, max_iter=5
		)

	
from crewai import Task

class OutreachTasks():
  def research_task(self, agent, participants, context,sender_information):
    return Task(
      description=dedent(f"""\
         Analyze the linkedin data of the prospect on linkedin to gather key points and insights, 
         focusing on information valuable for the best cold outreach.
			The Key points should be related to the my information only. Make sure to understand the date of the post.
        Outreach Prospect: {participants}
        Context: {context}
		  My Information:{sender_information}"""),
      agent=agent,
      expected_output=dedent("""A detailed report summarizing key findings about the prospect, highlighting information that could be relevant for the outreach, 
                             considering the outreach reason (context) provided. The report should be formatted in a clear and concise way, prioritizing the most valuable insights.
      Format:-'
         Key Points to talk about:-
         1.
         2.
         3.
         4.
         5.
         '
            """)
    )
   
  def email_strategy_task(self, agent, context, research):
      return Task(
         description=dedent(f"""\
         Develop a cold email for outreach to the prospect.

         Context: {context}
         Research Insights: {research}
         """), agent=agent,
         expected_output = dedent(f"""A hyper-personalized cold email (approximately 50 words) crafted by the email_specialist agent, 
                                  leveraging the key points and insights from the research report to achieve the specified outreach objective. 
                                 No pleasantries in the email.
                                 Placeholders:
                                 [ Casestudy ]: Placeholder for a relevant case study.
                                 [ YourName ]: Placeholder for the sender's name.
                                 [ Signature ]: Placeholder for the sender's signature.
                                 **Format:**
                                 ###Subject
                                 ### Body of the email
                                 **Example**:-'
                                             Here's an example format:

                                             ###Subject: [Compelling Subject Line related to Outreach Reason]

                                             ### Hi [Prospect Name],

                                             I noticed your recent post about [mention a relevant interest or challenge from the research]. At [Your Company], we help [briefly explain how your product/service addresses the prospect's needs].

                                             Would you be interested in a quick chat to learn more?

                                             Best,
                                             [Your Name]

                                             [Signature]
                                  '
                                  
         """)
      )

def main():
   from crewai import Crew
   tasks = OutreachTasks()
   agents = OutreachAgents()
   

   st.set_page_config("Cold Emails")
   st.header("Email Writer")

   print("## Welcome to the Outreach Planning Stage")
   print('-------------------------------')

   participants=st.text_area("Enter the prospect name here",max_chars=100)
   con=st.text_area("Why are you performing outreach:-",max_chars=10000)
   #objective=st.text_area("Enter the Objective of this outreach:-",max_chars=10000)
   sender_information=st.text_area("Enter your information:-",max_chars=10000)
   context={"Reason for the Outreach:- ",con," Sender Information:- ",sender_information}

   

   # Create Agents
   researcher_agent = agents.research_agent()
   email_specialist=agents.email_specialist()



   # Create Tasks
   research = tasks.research_task(researcher_agent, participants, context, sender_information)
   email = tasks.email_strategy_task(email_specialist, context,research)





   # Create Crew responsible for Copy
   crew = Crew(
      agents=[
         researcher_agent,
         email_specialist
      ],
      tasks=[
         research,
         email
      ]
   )

   if st.button("Submit & Process"):
      result = crew.kickoff()


      # Print results
      print("\n\n################################################")
      print("## Here is the result")
      print("################################################\n")
      print(result)

      with open("email.txt", "w") as file:
       file.write(str(result))
      st.write(result)

if __name__ == "__main__":
    main()

