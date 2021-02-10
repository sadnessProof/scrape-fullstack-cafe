# will be properly commented soon ;)


import os
import time
import json
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC



data_folder = './Data'
topics_xpath = '//*[@id="root"]/div/div[5]/div[2]/div/div/div/div'
sections_xpath = '//*[@id="root"]/div/div[5]/div[2]/div/div/nav[1]/div/div/div/button'
topic_css_selector = 'div.p-2.topic-questions-spacer'
question_css_selector = 'div.my-1.px-2.py-2.rounded.hovered'
answer_tag_css_selector = 'div.d-block.px-2'
question_tag_css_selector = 'div.col.justify-content-center.align-self-center.my-auto'


def wait_by_xpath(browser, xpath):
    """
    this method is waiting for xpath to load
    :param browser:
    :param xpath:
    :return:
    """
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        print('failed wait_xpath')


def wait_by_css_selector(browser, css_selector):
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    except TimeoutException:
        print('failed wait_css_selector')


def wait_by_class_name(browser, class_name):
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    except TimeoutException:
        print('failed wait_class_name')


def clear_directory(directory_address):
    """
    this method cleans passed directory
    :param directory_address:
    :return:
    """
    for file_name in os.listdir(directory_address):
        file_path = os.path.join(directory_address, file_name)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def setup_environment(dest_path):
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)
    else:
        clear_directory(dest_path)


def login():
    browser = webdriver.Edge(os.getcwd() + '\\' + 'msedgedriver.exe')
    
    # get to the fullctack.cafe's home page
    browser.get('https://www.fullstack.cafe/')
    time.sleep(40) # 40 secs to log in
    return browser


def section_topic_links(browser):
    topic_links = []
    wait_by_xpath(browser, topics_xpath)
    for topic in browser.find_elements_by_xpath(topics_xpath):
        topic_links.append(topic.find_element_by_xpath('./a[1]').get_attribute('href'))
    
    return topic_links

        
def get_section_elements(browser):
    wait_by_xpath(browser, sections_xpath)
    return browser.find_elements_by_xpath(sections_xpath)


def scrape_question(browser, q, is_challenge, a_json, q_json):
    global question_enumeration
    if 'Mid' in q.text:
        q_diff = 3
    if 'Entry' in q.text:
        q_diff = 1
    if 'Junior' in q.text:
        q_diff = 2
    if 'Senior' in q.text:
        q_diff = 4
    if 'Expert' in q.text:
        q_diff = 5

    q.find_element_by_xpath('./div/div/div[1]/span').click()
    q_text = q.find_element_by_xpath('./div/div/div[1]/h2').text

    q_json.append({
        'id': question_enumeration,
        'difficulty': q_diff,
        'title': q_text,
        'isChallenge': is_challenge
    })

    wait_by_css_selector(browser,answer_tag_css_selector)
    a_content = browser.find_element_by_css_selector(answer_tag_css_selector).get_attribute('innerHTML')

    a_json.append({
        'id': question_enumeration,
        'content': a_content,
        'slug': q_text
    })

    question_enumeration += 1
    q.find_element_by_xpath('./div/div/div[1]/span').click()


# Function to remove spaces  
# and convert into camel case 
def convert(s): 
    if(len(s) == 0): 
        return
    s1 = '' 
    s1 += s[0].upper() 
    for i in range(1, len(s)): 
        if (s[i] == ' '): 
            s1 += s[i + 1].upper() 
            i += 1
        elif(s[i - 1] != ' '): 
            s1 += s[i]  
    return s1


def scrape_section(browser, section_name, topic_links):
    section_name = str(section_name).strip()
    section_folder = data_folder+'/'+section_name
    os.mkdir(section_folder)
    # get all of the question for each topic
    for link in topic_links:
        browser.get(link)
        topic_name = link.split('/')[-1]
        
        answers_json = []
        questions_json = []

        wait_by_css_selector(browser, topic_css_selector)
        topic_questions = browser.find_element_by_css_selector(topic_css_selector).find_elements_by_xpath('./div')
        
        is_challenge = 0
        for question in topic_questions:

            if question.get_attribute('class') == 'my-2':
                is_challenge += 1
                pass

            wait_by_css_selector(browser, question_css_selector)
            if len(question.find_elements_by_css_selector(question_css_selector)):
                scrape_question(browser, question, is_challenge==2, answers_json, questions_json)
        
        topic_name = convert(topic_name.replace('-',' '))

        with open(f'{section_folder}/{topic_name}Answers.json', 'w') as outfile:
            json.dump(answers_json, outfile)
        
        with open(f'{section_folder}/{topic_name}Questions.json', 'w') as outfile:
            json.dump(questions_json, outfile)


def scrape_the_site(browser):
    section_names = []
    topic_links = []
    
    for section in get_section_elements(browser):
        section.click()
        section_names.append(section.text)
        topic_links.append(section_topic_links(browser))
        
    
    for i in range(0, len(section_names)):
        scrape_section(browser, section_names[i], topic_links[i])
        
    
def main():
    setup_environment(data_folder)
    # get to the fullctack.cafe's home page
    browser = login()
    browser.get('https://www.fullstack.cafe/')
    scrape_the_site(browser)
    browser.quit()


main()
