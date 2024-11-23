# AI_Brochures Application 🎨

<b> Create captivating business or organization brochures using website information </b>

Used advanced web scraping techniques using `BeautifulSoup` to scrape website information and pass it to `llama-70b` model to create a brochure that can be used for advertisements or major organisation events. Included a system prompt options to allow flexibility on specific type of brochure a user may need  

This app is currently hosted on <a href='https://huggingface.co/spaces/Koomemartin/AI_Brochures'>HuggingFace</a> Spaces


## Local Usage

Fork this repository and run the `app.py` script using the following code

First create a secure tunnel to run the streamlit app

```bash
wget -q -O - ipv4.icanhazip.com
```
This provides an IP address that autheticates you to access the app in your browser

```bash
streamlit run app.y & npx localtunnel --port 8501
```
This code runs the `app.y` in the secure tunnel and provides the link to acess it in your browser

```plain text
Utilized Groq free API to call the llma model
```

<a href='https://console.groq.com/'>Sign up</a> for a Groq account



