from selenium import webdriver
from bs4 import BeautifulSoup

import math
import csv

from time import sleep

target_roles = [
    'data analyst', 
    'data scientist', 
    'software engineer', 
    'data engineer', 
    'database administrator', 
    'machine learning engineer', 
    'research analyst', 
    'operations analyst', 
    'web designer', 
    'java developer'
    ]

base_url = 'https://www.naukri.com/'

options = webdriver.EdgeOptions()
options.add_argument("--disable-logging")
options.add_argument('--log-level=3')

driver = webdriver.Edge(options = options)

def getPageNumber(soup):
    no_of_posts = int(soup.find('div', class_ = 'styles_h1-wrapper__mHVA1').span.text.split("of ")[1])
    return no_of_posts, math.ceil(no_of_posts/20)

def getPostURLs(soup):
    hrefs = []
    for title in soup.find_all('a', class_ = 'title'):
        if title.attrs.get('href'):
            hrefs.append(title.attrs.get('href'))
    return hrefs

for target_role in target_roles:
    print(f"Scraping {target_role} job posts from Naukri.com ... ")
    with open(f"datasets/{target_role}.csv", 'w', newline= '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Job Title',
            'URL',
            'Company Name',
            'Work Mode',
            'Experience Required',
            'Salary',
            'Location',
            'Post Rating',
            'No. of Reviews',
            'Post Age',
            'Job Openings',
            'No. of Applicants',
            'Role Name',
            'Industry Type',
            'Department',
            'Employment Type',
            'Role Category',
            'UG Requirements',
            'PG Requirements',
            'Skills Required'
        ])
        url = f"{base_url}{'-'.join(target_role.split(' '))}-jobs"

        driver.get(url)
        sleep(3)

        listings_soup = BeautifulSoup(driver.page_source, 'html.parser')

        no_of_posts, no_of_pages = getPageNumber(listings_soup)
        print(f"Found a total of {no_of_posts} posts i.e {no_of_pages} pages of posts.")

        for no in range(1,  2):#no_of_pages + 1
            count = 0
            page_url = f"{url}-{no}"

            driver.get(page_url)
            sleep(3)

            page_soup = BeautifulSoup(driver.page_source, 'html.parser')

            hrefs = getPostURLs(page_soup)
            for link in hrefs:
                try:
                    driver.get(link)
                    sleep(1.5)

                    post_soup = BeautifulSoup(driver.page_source, 'html.parser')

                    if post_soup.find('div', class_ = 'styles_jhc__jd-top-head__MFoZl') != None:
                        title = post_soup.find('div', class_ = 'styles_jhc__jd-top-head__MFoZl').h1.text
                    else:
                        title = None

                    if  post_soup.find('div', class_ = 'styles_jd-header-comp-name__MvqAI') != None:
                        company = post_soup.find('div', class_ = 'styles_jhc__jd-top-head__MFoZl').a.text

                    else:
                        company = None
                    print(company)

                    if post_soup.find('div', class_ = 'styles_jhc__exp__k_giM')!=None:
                        experience = post_soup.find('div', class_ = 'styles_jhc__exp__k_giM').span.text
                    else:
                        experience = None

                    if post_soup.find('div', class_ = 'styles_jhc__salary__jdfEC')!= None:
                        salary = post_soup.find('div', class_ = 'styles_jhc__salary__jdfEC').span.text
                    else:
                        salary = None

                    if post_soup.find('div', class_ = 'styles_jhc__wfhmode__iQwF4')!= None:
                        wfhType = post_soup.find('div', class_ = 'styles_jhc__wfhmode__iQwF4').span.text
                    else:
                        wfhType = None
                    
                    if post_soup.find('span', class_ = 'styles_jhc__location__W_pVs')!=None:
                        location = post_soup.find('span', class_ = 'styles_jhc__location__W_pVs').text
                    else:
                        location = None

                    if post_soup.find('span', class_ = 'styles_amb-rating__4UyFL')!=None:
                        rating = post_soup.find('span', class_ = 'styles_amb-rating__4UyFL').text
                    else:
                        rating = None

                    if post_soup.find('span', class_ = 'styles_amb-reviews__0J1e3')!=None:
                        n_reviews = post_soup.find('span', class_ = 'styles_amb-reviews__0J1e3').text
                    else:
                        n_reviews = None

                    post_status = []
                    for status in post_soup.find_all('span', class_ = 'styles_jhc__stat__PgY67'):
                        post_status.append(status.text)
                    
                    post_age = post_status[0].replace('Posted: ','')
                    openings = int(post_status[1].replace('Openings: ',''))
                    n_applicants = int(post_status[2].replace('Applicants: ',''))

                    temp = []
                    for info in post_soup.find_all('div', class_ = 'styles_details__Y424J'):
                        temp.append(info.text)
                    if len(temp) == 6:
                        role, industry_type, dept, emp_type, role_category, undergrad = tuple(temp)
                        postgrad = None
                    if len(temp) == 7:
                        role, industry_type, dept, emp_type, role_category, undergrad, postgrad = tuple(temp)

                    role = role.replace('Role: ','').replace(',','')
                    industry_type = industry_type.replace('Industry Type: ','').replace(',','')
                    dept = dept.replace('Department: ', '').replace(',','')
                    emp_type = emp_type.replace('Employment Type: ','')
                    role_category = role_category.replace('Role Category: ', '')

                    if undergrad:
                        undergrad = undergrad.replace('UG: ','')
                    else:
                        undergrad = None

                    if postgrad:
                        postgrad = postgrad.replace('PG: ','')
                    else:
                        postgrad = None

                    skills = []
                    for skill in post_soup.find_all('a', class_ = ['styles_chip__7YCfG styles_non-clickable__RM_KJ','styles_chip__7YCfG styles_clickable__dUW8S']):
                        skills.append(skill.text)
                    skills = ", ".join(skills)
                    
                    writer.writerow([ title, link, company, wfhType, experience, salary, location, rating, n_reviews, post_age, openings, n_applicants, role, industry_type, dept, emp_type, role_category, undergrad, postgrad, skills])
                    
                    count += 1

                except:
                    with open('datasets/errors.csv', 'w', newline='') as errorfile:
                        error_writer = csv.writer(errorfile)
                        error_writer.writerow([link, role])
                        continue  
                      
        print(f"Successfully scraped {count} {target_role} posts out of {no_of_posts} posts!")

        

