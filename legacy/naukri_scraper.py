# from selenium import webdriver
# from bs4 import BeautifulSoup
# import time

# base_url = 'https://www.naukri.com/'

# roles = ['data analyst']
# work_modes = ['Work from office', 'Hybrid', 'Remote']
# salary_ranges = ['0-3 Lakhs', '3-6 Lakhs', '6-10 Lakhs', '10-15 Lakhs', '15-25 Lakhs', '25-50 Lakhs', '50-75 Lakhs', '75-100 Lakhs', '1-5 Cr']

# # for role in roles:
# #     role_url = base_url
# #     role_url = f"{base_url}{'-'.join(role.split(' '))}-jobs"
# #     print("Role Url", role_url)

# #     for work_mode_index, work_mode in enumerate(work_modes):
# #         work_mode_url = role_url
# #         work_mode_url = f"{role_url}?wfhType={work_mode_index}"
# #         print("Work Mode Url", work_mode_url)   

# driver=webdriver.Edge()
# driver.get('https://www.naukri.com/data-analyst-jobs')
# time.sleep(4)
# soup = BeautifulSoup(driver.page_source, 'html.parser')
# print(soup.find('div', class_ = 'styles_h1-wrapper__mHVA1'))
import json

print(json.loads("{'class': ['title'], 'title': 'Data Analyst', 'href': 'https://www.naukri.com/job-listings-data-analyst-healthsy-coimbatore-1-to-3-years-130624502000', 'target': '_blank', 'rel': ['noopener', 'noreferrer']}".replace("'", '"'))['href'])