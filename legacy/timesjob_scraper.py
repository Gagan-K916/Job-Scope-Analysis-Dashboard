#NOTE this is the completed verison of the code to scrape across salary range and job type filter in times job

#NOTE here we are adding a pagination which was previously missing in our code also add 20 and 50 lakhs

import time
from bs4 import BeautifulSoup
import requests
import os
import csv
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Taking user input for the keyword
logging.info(">>>>> Enter the job keyword you want to search for <<<<<")
job_keyword = input('>').strip()  # Remove any leading/trailing whitespace

BASE_URL = 'https://www.timesjobs.com/candidate/job-search.html'

# Define filter parameters
salary_ranges = [
    ('0', '200000', '0-2 Lakhs'), 
    ('200000', '400000', '2-4 Lakhs'), 
    ('400000', '600000', '4-6 Lakhs'), 
    ('600000', '1000000', '6-10 Lakhs'), 
    ('1000000', '1500000', '10-15 Lakhs'),
    ('1500000', '2500000', '15-25 Lakhs'),
    ('2500000', '5000000', '25-50 Lakhs'),
    ('5000000', '', '50+Lakhs'),
]
job_types = {
    'regular': 'n',
    'work-from-home': 'y'
}

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_applicants_count(job_url):
    driver = setup_driver()
    driver.get(job_url)
    
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "jobInsightApplyCount"))
        )
        
        applicants_text = element.text.strip()
        match = re.search(r'\d+', applicants_text)
        if match:
            applicants_number = int(match.group())
            return applicants_number
        else:
            return 'N/A'
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'N/A'
    finally:
        driver.close()
        driver.quit()

def save_job_data_csv(job_data):
    try:
        os.makedirs('data', exist_ok=True)
        #<<<<PLEASE ADJUST THE CSV FILE NAME ACCORDING TO WHAT IS BEING SCRAPED >>>>
        filename = 'Machine Learning Engineer.csv'
        file_exists = os.path.isfile(filename)

        with open(filename, 'a', newline='') as csvfile:
            field_names = [
                'Index', 'Page Number', 'Company Name', 'Job Description', 'Skills Required', 
                'Location', 'Experience', 'Job Posted', 'More Info', 'Applicants', 'Specialization', 
                'Qualification', 'Employment Type', 'Company Website', 'Company Industry', 
                'Salary Range', 'Job Type'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=field_names)

            if not file_exists:
                writer.writeheader()

            writer.writerow(job_data)

        logging.info(f"Job data saved successfully: {job_data}")

    except Exception as e:
        logging.error(f"Failed to save job data: {e}")

def extract_experience_and_location(job):
    experience = ''
    location = ''
    
    details = job.find('ul', class_='top-jd-dtl clearfix')
    if details:
        details = details.find_all('li')
        for detail in details:
            if 'card_travel' in detail.text:
                experience = detail.find('span').text.strip() if detail.find('span') else detail.text.replace('card_travel', '').strip()
            elif 'location_on' in detail.text:
                location = detail.find('span').text.strip() if detail.find('span') else detail.text.strip()
    
    return experience, location

def scrape_job_details(more_info_url):
    logging.info(f"Scraping job details from {more_info_url}")
    response = requests.get(more_info_url)
    soup = BeautifulSoup(response.text, 'lxml')

    specialization = ''
    qualification = ''
    employment_type = ''
    company_website = 'No link found'  # Default value if website is not found
    company_industry = ''

    qualification_tag = soup.find('label', text='Qualification:')
    if qualification_tag:
        qualification = qualification_tag.find_next('span').text.strip()

    specialization_tag = soup.find('label', text='Specialization:')
    if specialization_tag:
        specialization = specialization_tag.find_next('span').text.strip()

    employment_type_label = soup.find('label', text='Employment Type:')
    if employment_type_label and employment_type_label.next_sibling:
        employment_type = employment_type_label.next_sibling.strip()
    
    industry_name_element = soup.find('label', text='Industry:')
    company_industry = industry_name_element.find_next_sibling('span').get_text(strip=True) if industry_name_element else 'Industry name not found.'

    # Improved logic to find the company website
    apply_flow_div = soup.find('div', class_='jd-sec jd-hiring-comp', id=lambda x: x and x.startswith('applyFlowHideDetails_'))
    if apply_flow_div:
        ul = apply_flow_div.find('ul', class_='hirng-comp-oth clearfix')
        
        if ul:
            for li in ul.find_all('li'):
                label = li.find('label')
                if label and label.text.strip() == 'Website':
                    company_website_link = li.find('a', href=True)
                    if company_website_link:
                        company_website = company_website_link['href']

    # Ensure the link is valid and not a generic URL
    if company_website == 'No link found' or 'companySearchResult.html' in company_website:
        company_website = 'No link found'

    logging.info(f"Company Website: {company_website}")
    
    return specialization, qualification, employment_type, company_website, company_industry

def generate_filter_urls(base_url, keyword):
    urls = []
    for salary in salary_ranges:
        for job_type, remote_job in job_types.items():
            url = f"{base_url}?clusterName=CLUSTER_CTC&refineBy=dateWise&from=undo&luceneResultSize=25&txtKeywords={keyword}&postWeek=60&searchType=personalizedSearch&actualTxtKeywords={keyword}&remoteJob={remote_job}&txtLowSalary={salary[0]}&txtHighSalary={salary[1]}"
            urls.append((url, salary[2], job_type))
    return urls

def scrape_filtered_jobs(filter_urls):
    for url, salary_range, job_type in filter_urls:
        scrape_jobs_from_url(url, salary_range, job_type)

def scrape_jobs_from_url(url, salary_range, job_type):
    logging.info(f"Scraping URL: {url}")
    page_num = 1
    seen_jobs = set()
    
    while True:
        response = requests.get(url + f"&sequence={page_num}")
        soup = BeautifulSoup(response.text, 'lxml')

        jobs = soup.find_all('li', class_="clearfix job-bx wht-shd-bx")
        
        if not jobs:
            logging.info("No jobs found on this page.")
            break

        new_jobs = [job for job in jobs if job not in seen_jobs and job_keyword.lower() in job.header.h2.a.text.lower()]
        if not new_jobs:
            logging.info("No new jobs found, ending scrape for this filter combination.")
            break
        
        for index, job in enumerate(new_jobs): 
            try:
                company_name = job.find('h3', class_='joblist-comp-name').text.strip()
                job_desc = job.find('label', string='Job Description:')
                job_desc = job_desc.next_sibling.strip() if job_desc else 'No description available'
                skill_needed = job.find('span', class_='srp-skills').text.replace(" ", "").lower()
                experience, location = extract_experience_and_location(job)
                date = job.find('span', class_='sim-posted').text.strip()
                more_info = job.header.h2.a['href']
                applicants = get_applicants_count(more_info)

                specialization, qualification, employment_type, company_website, company_industry = scrape_job_details(more_info)
                
                skills_list = skill_needed.split(',')

                job_data = {
                    'Index': index,
                    'Page Number': page_num,
                    'Company Name': company_name,
                    'Job Description': job_desc.strip(),
                    'Skills Required': ', '.join(skills_list).strip(),
                    'Location': location,
                    'Experience': experience,
                    'Job Posted': date,
                    'More Info': more_info,
                    'Applicants': applicants,
                    'Specialization': specialization,
                    'Qualification': qualification,
                    'Employment Type': employment_type,
                    'Company Website': company_website,
                    'Company Industry': company_industry,
                    'Salary Range': salary_range,
                    'Job Type': job_type
                }
                
                save_job_data_csv(job_data)
                seen_jobs.add(job)

            except Exception as e:
                logging.error(f"Error processing job: {e}")

        page_num += 1
        time.sleep(2)

if __name__ == "__main__":
    filter_urls = generate_filter_urls(BASE_URL, job_keyword)
    scrape_filtered_jobs(filter_urls)



