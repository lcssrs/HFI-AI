# The idea of this script is to mine the data from the website of the European Central Bank and save it in a csv file. The script should be executable to overscribe the original csv file and update the dataset.
# There are no inputs 
# The ouput should be a csv file with two columns: The date of the monetary policy decision and the text contained in the press release

#Loading packages
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import re
import pandas as pd

#Establishing the websites where each piece of information will be scrapped from. Then scrap the dates of each ECB meeting


#################### SELECTING THE PAGES THAT WILL BE SCRAPPED FROM THE MAIN PAGE ############################################

#We have to use selenium library because ECB's website is of the type scroll and load, therefore the code is not all there
# in the simple html version, in this code we open the website and scroll down until we get the whole source code

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Target URL
url = "https://www.ecb.europa.eu/press/govcdec/mopo/html/index.en.html"

# Configure Chrome driver 
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the URL
driver.get(url)

driver.maximize_window()

driver.get(url)

last_height = 0

#loop that scrolls the page down until the full source code appears

while True:
    driver.execute_script('window.scrollBy(0, 5000)')
    time.sleep(2)

    new_height = driver.execute_script("return document.body.scrollHeight")
    print(str(new_height)+"-"+str(last_height))

    if(new_height == last_height):
        break

    else:
        last_height = new_height

# Get the complete HTML content
html_content = driver.page_source

#Creating the soup
soup = BeautifulSoup(html_content, "html.parser")


# Quit the browser
driver.quit()

################## GETTING LINK FOR EACH PAGE ######################################

# Regular expression pattern to match the desired links
pattern = re.compile(r'^/press/pr/date/\d{4}/html/.*\.en\.html$')

# Set to keep track of unique links
unique_links = set()

# List to store the first occurrences since the links appear repeated times
first_occurrences = []

# Find all 'a' tags with 'href' attribute
for a_tag in soup.find_all('a', href=True):
    href = a_tag['href']
    # Check if the link matches the pattern
    if pattern.match(href) and href not in unique_links:
        unique_links.add(href)
        first_occurrences.append(href)

        
#######################################################

# Regular expression pattern to match the desired links
pattern = re.compile(r'^/press/pr/date/\d{4}/html/.*\.en\.html$')

# Set to keep track of unique links
unique_links = set()
# List to store the first occurrences
first_occurrences = []

# Find all 'a' tags with 'href' attribute
for a_tag in soup.find_all('a', href=True):
    href = a_tag['href']
    # Check if the link matches the pattern
    if pattern.match(href) and href not in unique_links:
        unique_links.add(href)
        first_occurrences.append(href)

############# SAVING THE TEXT CONTENT OF EACH PAGE ####################################

#Preallocating the list to save the content
text_strings = [None]*len(first_occurrences)

#Loop that fills the list with the text from each of the ECB's meetingS
for i in range(len(first_occurrences)):
    test = first_occurrences[i]

    link = 'https://www.ecb.europa.eu' + test

    response = requests.get(link)
    html = response.text

    #Creating Beautiful Soup object
    soup = BeautifulSoup(html, 'html.parser')

    #Navigating to where the main text is located
    page_text = soup.body.main.get_text(separator=' ', strip=True)

    #Saving the text
    text_strings[i]=page_text

############ BASIC PREPROCESING OF THE DATA AND CSV CREATION ###############

# Regular expression to match the pattern and capture the date and the rest of the text
pattern = re.compile(r"(PRESS RELEASE Monetary policy decisions \d{1,2} \w+ \d{4})(.*?)(CONTACT.*)", re.DOTALL)

# Dictionary to map month names to month numbers
month_mapping = {
    "January": "01", "February": "02", "March": "03", "April": "04",
    "May": "05", "June": "06", "July": "07", "August": "08",
    "September": "09", "October": "10", "November": "11", "December": "12"
}

def convert_date_format(date_str):
    # Match the date pattern within the extracted date part
    date_match = re.search(r"(\d{1,2}) (\w+) (\d{4})", date_str)
    if date_match:
        day = date_match.group(1).zfill(2)
        month = month_mapping[date_match.group(2)]
        year = date_match.group(3)
        return f"{day}/{month}/{year}"
    return None

# Lists to store formatted dates and remaining texts
dates = []
texts_after_date = []

# Extract dates and remaining texts
for text in text_strings:
    match = pattern.match(text)
    if match:
        date_str = match.group(1)
        remaining_text = match.group(2).strip()
        formatted_date = convert_date_format(date_str)
        dates.append(formatted_date)
        texts_after_date.append(remaining_text)

# Create a DataFrame
df = pd.DataFrame({
    'Date': dates,
    'Text': texts_after_date
})

#Saving as a csv file
df.to_csv('press_release.csv', encoding='utf-8')