import streamlit as st
from bs4 import BeautifulSoup
import requests
from groq import Groq
from dotenv import load_dotenv
import os
import json

# scraping pipeline
class Website:
    """
    A utility class to represent a Website that we have scraped
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]  # links found in home page
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"


# first lets get relevant links from the home page for a broad information about the website provided

# system prompt of the first call 
link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to include in a brochure about the company, \
such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
link_system_prompt +="Kindly avoid selecting email links with this: \n mailto:company@gmail.com \n "
link_system_prompt += "You should respond in JSON as in this example:"
link_system_prompt += """
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page": "url": "https://another.full.url/careers"}
    ]
}
"""

#pre defined user prompt to extract only important links in about the website 
def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links to the website, respond with the full https URL in JSON format. \
                    Do not include Terms of Service, Privacy\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt

# make the first call to get the important links 
def get_links(url):
    website = Website(url)
    response = client.chat.completions.create(
    messages=[
       {"role": "system", "content":link_system_prompt },
       {"role": "user", "content": get_links_user_prompt(website)}
    ],
    model="llama3-groq-70b-8192-tool-use-preview",
    temperature=1,
    max_tokens=2048,
    stop=None,
    stream=False,
    response_format = {"type" : "json_object" })
    result = response.choices[0].message.content
    return json.loads(result)

#all the content required to generate information from user about the website
@st.cache_resource
def get_all_details(url):
    result = "Home page:\n"
    result += Website(url).get_contents()
    links = get_links(url)
    print("Available links:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result

    
system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
Include details of company culture, customers and careers/jobs if you have the information."

def second_call_sytem_prompt(system=None):
    if system:
        return system
    else:
        return system_prompt


def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown and provide usable links in the contacts areas \n"
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:20_000] # Truncate if more than 20,000 characters
    return user_prompt

# Initialize Groq client
load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

# Streamlit UI
st.title("AI Brochures 🎨📌")
st.write("Create a captivating brochure of your company or institution by only using information from your website!!")

# Input fields
system= st.text_input("Modify the model response using a custom system prompt if not satisfied with generated response:" , " "  )
url = st.text_input("Provide the Company's website URL:", " " )
user_query = st.text_area("Provide a title for the brochure or the name of the organization")

if user_query:
    # Scrape website content
    with st.spinner("Scraping website..."):
        
        try:
            second_user_prompt = get_brochure_user_prompt(user_query, url)
            st.success("Website loaded successfully!")
        except Exception as e:
            st.error(f"Failed to load website: {e}")
        
        # Second to Call Groq API for processing
        st.write("Querying the website...")
        with st.spinner("Processing your query..."):
            try:
                chat_streaming = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": second_call_sytem_prompt()},
                        {"role": "user", "content": second_user_prompt}
                    ],
                    model="llama3-groq-70b-8192-tool-use-preview",
                    temperature=0.8,
                    max_tokens=2042,
                    top_p=0.6,
                    stream=False,
                )
                # st.write('Passed model')

            except Exception as e:
                st.error(f"Failed to process query to model: {e}")
            response = ""
            try:
                # for chunk in chat_streaming:
                #     content = chunk.choices[0].delta.content
                #     if content:  # Ensure content is not None
                response=chat_streaming.choices[0].message.content
                # response += content
                st.write("🤖:")
                st.write(response)
            except Exception as e:
                st.error(f"Failed to process query: {e}")



st.markdown("--------------")
st.write("© 2024 Application")
