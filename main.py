import os
import time
import json
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


def wait_by_class_name(browser, class_name):
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    except TimeoutException:
        print('failed wait_class_name')


def wait_by_css_selector(browser, css_selector):
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    except TimeoutException:
        print('failed wait_css_selector')


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


def scrape_question(q, q_id, is_challenge, a_json, q_json):
    wait_by_css_selector(q,'h2.question-topic-header-title.font-weight-bold')
    wait_by_css_selector(q,'span.clickable.badge.badge-difficulty-1')
    
    q_diff = q.find_element_by_css_selector('span.clickable.badge.badge-difficulty-1')
    q = q.find_element_by_css_selector('h2.question-topic-header-title.font-weight-bold')
    q.click()
    
    q_json.append({
        'id': q_id,
        'difficulty': q_diff,
        'tittle': q.text,
        'isChallenge': is_challenge
    })
    
    
    
    wait_by_css_selector(browser,answer_tag_css_selector)
    a_content = browser.find_element_by_css_selector(answer_tag_css_selector).get_attribute('innerHTML')
    
    a_json.append({
        'id': q_id,
        'content': a_content,
        'slug': q.text
    })

    q_id += 1
    q.click()



browser = webdriver.Edge(os.getcwd() + '\\' + 'msedgedriver.exe')

# get to the fullctack.cafe's home page
browser.get('https://www.fullstack.cafe/')

print('start counting')
time.sleep(40)
print('end counting')

data_folder = './Data'
setup_environment(data_folder)


# # necessary variables
topics_xpath = '//*[@id="root"]/div/div[5]/div[2]/div/div/div/div'
sections_xpath = '//*[@id="root"]/div/div[5]/div[2]/div/div/nav[1]/div/div/div/button'
topic_css_selector = 'div.p-2.topic-questions-spacer'
question_css_selector = 'div.my-1.px-2.py-2.rounded.hovered'
answer_tag_css_selector = 'div.d-block.px-2'
question_tag_css_selector = 'div.col.justify-content-center.align-self-center.my-auto'
question_enumeration = 1



# get section elements (Full-Stack, Web & Mobile | System Design & Architecture | Coding & Data Structures) 
wait_by_xpath(browser, sections_xpath)
sections = browser.find_elements_by_xpath(sections_xpath)


# iterate them to scrape
for section in sections:
    section.click()
    section_folder = data_folder+'/'+section.text
    os.mkdir(section_folder)
    
    # get topics for each section
    wait_by_xpath(browser, topics_xpath)
    topic_container = browser.find_elements_by_xpath(topics_xpath)
    
    for topic in topic_container:
        topic.click()
        topic_name = browser.current_url.split('/')[-1]
        
        answers_json = []
        questions_json = []
        
        # get all of the question for each topic
        wait_by_css_selector(browser, topic_css_selector)
        topic_questions = browser.find_element_by_css_selector(topic_css_selector).find_elements_by_xpath('./div')
        
        # iterate divs in the questions container
        is_challenge = 0
        for question in topic_questions:
            if question.get_attribute('class') == 'my-2':
                is_challenge += 1
                pass
            
            wait_by_css_selector(browser, question_css_selector)
            q_tag = question.find_elements_by_css_selector(question_css_selector)
            if len(q_tag):
                scrape_question(q_tag[0], question_enumeration, is_challenge==2, answers_json, questions_json)
       
        with open(f'{section_folder}/{topic_name}-answers.json', 'w') as outfile:
            json.dump(answers_json, outfile)
        
        with open(f'{section_folder}/{topic_name}-questions.json', 'w') as outfile:
            json.dump(questions_json, outfile)