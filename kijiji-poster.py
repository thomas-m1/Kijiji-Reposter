#!/usr/bin/env python3.9.5
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from fake_useragent import UserAgent
import json
import os
import sys
import time


class Kijiji(object):
    
    def __init__(self, sysArgs):
        self.argumentList = sysArgs
        self.argumentList_length = len(sys.argv)

        self.main_folder_path = os.path.dirname(__file__)
        self.ad_folder_path = os.path.join(self.main_folder_path, 'kijiji_ads')
        
        #user credentials
        self.username = ""
        self.password = ""
        self.login_file = "login-info.json"
        self.attempts = 2
        self.max_page = 1
        self.max_replies = 0
        self.current_ad_title = None
        self.failed_postings = []
        self.successfull_postings = []
        self.deleted_ads = []
        self.failed_deleted_ads = []
        self.error_file = []
        self.set_up()
    
    
    # uses random user agents that enables some features to bypass kijiji bot detection, and sets up driver
    def set_up(self):
        self.options = Options()
        # adding in user agents
        self.agent = UserAgent()
        self.userAgent = self.agent.random
        
        # setting options - add user agent, set automation to false - bypasses bot
        self.options.add_argument(f'user-agent={self.userAgent}')
        self.options.add_argument("disable-blink-features=AutomationControlled");
        self.options.add_experimental_option('useAutomationExtension', False)
        # self.options.add_argument('--headless')
        # self.options.add_argument("--window-size=1920,1080")
        # PROXY = "109.195.69.211:8090"
        # self.options.add_argument('--proxy-server=%s' % PROXY)
        
        #set chrome driver. update this to where your driver is located. you can set the driver to be in your folder
        Chrome_driver_path = os.path.join(self.main_folder_path, 'chromedriver.exe')
        self.driver = webdriver.Chrome(chrome_options = self.options, executable_path = Chrome_driver_path)
        
        self.login()
    
    
    # function to wait until new url is opened
    def next_url(self, new_url):
        current = self.driver.current_url
        self.driver.get(new_url)
        WebDriverWait(self.driver, 30).until(EC.url_changes(current))
    
    
    #function to wait until new url is opened after a click
    def next_click(self, next_click):
        current = self.driver.current_url
        next_click.click()
        WebDriverWait(self.driver, 30).until(EC.url_changes(current))
    
    
    # opens the chrome browser, goes to kijiji home and logs into user account
    def login(self):
        
        # opens kijiji home page
        self.next_url('https://www.kijiji.ca/')
        
        # finds the sign in link and clicks
        sign_in_button = self.driver.find_element_by_xpath("//a[@title='Sign In']")
        self.next_click(sign_in_button)
        time.sleep(1)
        
        
        # gets user login information from json file
        os.chdir(self.main_folder_path)
        try:
            with open(self.login_file, 'r') as f: # reads and stores data from json
                loginInfo = json.load(f)
                self.password = loginInfo['password']
                self.username = loginInfo['username']
            time.sleep(1)
        except:
            print("error with {} file: unable to retreive login information".format(self.login_file)+str(IOError))
            self.failed_postings.append(self.login_file)
            pass
        
        
        # enters user credentials
        #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'emailOrNickname'))).send_keys(self.username)
        emailOrNickname = self.driver.find_element_by_name('emailOrNickname')
        emailOrNickname.send_keys(self.username)
        password_prompt = self.driver.find_element_by_name('password')
        password_prompt.send_keys(self.password)
        time.sleep(0.5)
        
        # click sign in button
        sign_in = self.driver.find_element_by_xpath("//*[@id='LoginForm']/button")
        #self.next_click(sign_in)
        sign_in.click()
        self.argument_handle()
    
    
    # prints the results of the program
    def results_and_exit(self):
            print("Ending process...")
            print("there is an error with the following files: ")
            print(', '.join(self.error_file))
            print("\nyou have successfully posted: ")
            print(', '.join(self.successfull_postings))
            print("\nyou have failed to post: ")
            print(', '.join(self.failed_postings))
            print("failed to delete the following ads: ")
            print(', '.join(self.failed_deleted_ads))
            print("successfully deleted the following ads: ")
            print(', '.join(self.deleted_ads))
            print("goodbye!")
            self.driver.quit()
            exit()
    
    
    # if the user includes argument in the command line, can execute using the argument
    # can use this with bash scripts to automate task may not always work because of captcha
    def argument_handle(self):
        #user can choose the file they want to post  
        if self.argumentList_length > 1:
            user_input = ' '.join(self.argumentList[1:])
            print("now executing: " + user_input)
            time.sleep(2)
            
            # attempts to connect x times
            for x in range(0,self.attempts):
                try:
                    self.user_prompt(user_input)
                except Exception as err:
                    self.attempts = self.attempts+1
                    print(f"attempt #: {self.attempts}")
                    print("failed to use command line argument")
                    self.driver.quit()
                    time.sleep(2)
                    self.set_up()
            raise err
        
        else: # switches to user input
            while True:
                user_input = input("Enter command: ").lower()
                self.user_prompt(user_input)
    
    
    # driver, user pick the files to post
    def user_prompt(self, user_input):
        
        os.chdir(self.ad_folder_path)
        if user_input.startswith("post") & user_input.endswith("all"):# posts all ads in directory
            print('posting all ads from kijiji_ads folder:')
            for files in os.listdir():# print list of ads
                print(files)
            for ad in os.listdir():# post each ad
                try:
                    print("Now posting ad from: {}".format(ad))
                    data = self.get_json_data(ad)
                    if data != False:
                        self.post_ad(ad,data)
                    else:
                        print('error with file: {}. Try again.'.format(user_input))
                        self.error_file.append(user_input)
                except:
                    print('error with file: {}. Try again.'.format(ad))
                    self.error_file.append(ad)
                    pass
            print("Failed to post the following files: ")
            print(', '.join(self.failed_postings))
        
        # deletes postings
        elif user_input.startswith("delete") & user_input.endswith("all"):# deletes files
            print('deleting all ads from kijiji_ads folder:')
            for files in os.listdir():# print list of ads
                print(files)
            for ad in os.listdir():# delete each ad
                try:
                    print("Now deleting ad from: {}".format(ad))
                    data = self.get_json_data(ad)
                    if data != False:
                        self.delete_ads(ad,data)             
                    else:
                        print('error with file: {}. Try again.'.format(user_input))
                        self.error_file.append(user_input)
                except:
                    print('error with file: {}. Try again.'.format(ad))
                    self.error_file.append(ad)
                    pass
            print("deleted the following ads: ")
            print(self.deleted_ads)
        
        # deletes and posts all ads in directory
        elif user_input == "delete and post":
            try:
                print('deleting and posting all ads from kijiji_ads folder:')
                for files in os.listdir():# print list of ads
                    print(files)
                for ad in os.listdir():# delete each ad
                    try:
                        print("Now deleting ad from: {}".format(ad))
                        data = self.get_json_data(ad)
                        if data != False:
                            self.delete_ads(ad,data)
                        else:
                            print('error with file: {}. Try again.'.format(ad))
                            self.error_file.append(ad)
                    except:
                        print('error with file: {}. Try again.'.format(ad))
                        self.error_file.append(ad)
                        pass
            except:
                print("error with deleting")

            print("failed to delete the following ads: ")
            print(self.failed_deleted_ads)
            print("successfully deleted the following ads: ")
            print(self.deleted_ads)
            
            # now posting ads
            try:
                for ad in os.listdir():# post each ad
                    try:
                        print("Now posting ad from: {}".format(ad))
                        data = self.get_json_data(ad)
                        if data != False:
                            self.post_ad(ad,data)
                        else:
                            print('error with file: {}. Try again.'.format(user_input))
                            self.error_file.append(user_input)
                    except:
                        print('error with file: {}. Try again.'.format(ad))
                        self.error_file.append(ad)
                        pass        
            except:
                print("error with posting")
                
            print("Failed to post the following files: ")
            print(', '.join(self.failed_postings))
            print("you have successfully posted: ")
            print(', '.join(self.successfull_postings))
        
        
        # post single file
        elif os.path.exists(user_input):#posts single ad in directory
            
            data = self.get_json_data(user_input)
            if data != False:
                try:
                    self.post_ad(user_input, data)             
                except:
                    print("failed to post: {}".format(user_input))
                    pass
                print("Failed to post the following files: ")
                print(', '.join(self.failed_postings))
            else:
                print('error with file: {}. Try again.'.format(user_input))
                self.error_file.append(user_input)
        
        # prints results, exits program
        elif user_input == "f" or user_input == "exit" or user_input == "end":# ends process
            self.results_and_exit()
        
        # return message if input invalid
        else:
            print("Invalid input. Please try again:\npost all: posts all ads in directory\n'delete all': deletes all ads in directory from kijiji\n'delete and post': combination of deleting and reposting the ads from the folders on kijiji\n'<ad_file>': just enter the name of the file you want to post by itself\n'f' or 'exit' or 'end': finishes the script and returns results")
    
    
    # reads json files in directory
    def get_json_data(self, ad):
        os.chdir(os.path.join(self.ad_folder_path, ad))# change to image directory
        # opens json file in the folder
        try:
            for file in os.listdir():
                if file.endswith(".json"):
                    ad_json = file
                    break
            with open(ad_json, 'r') as f: # reads and stores data from json
                data = json.load(f)
            time.sleep(1)
            return data
        except:
            print("error with {} file: ".format(ad)+str(IOError))
            self.failed_postings.append(ad)
            return False
    
    
    # deletes ads and gets stats before deleting
    def delete_ads(self, ad, data):
        
        self.next_url("https://www.kijiji.ca/m-my-ads/active/")
        time.sleep(2)
        
        # finds the ad and clicks on it
        ad_to_delete = self.driver.find_element_by_xpath("//*[contains(text(), '{}')]".format(data['ad_title']))
        ad_to_delete.click()
        time.sleep(2)
        ad_stats = []
        
        # gets stats for the ad
        count = self.driver.find_elements_by_xpath(".//span[starts-with(@class, 'count-')]")
        for stats in count:
            ad_stats.append(stats.text)
        visits = int(ad_stats[0])
        page = int(ad_stats[1])
        replies = int(ad_stats[2])
        print("results for posting {}".format(ad))
        print("visits : "+visits)
        print("page # : "+page)
        print("replies: "+replies)
        
        # checks if there are any replies and what page it is on, if no replies and is on page 2 or further, delete it
        if replies >= self.max_replies & page >= self.max_page:
            print("deleting ad: '{}'\nad is in folder: {}".format(data['ad_title'], ad))
            #delete ad
            #delete = self.driver.find_elements_by_xpath("//*[@id='ViewItemPage']/div[2]/div/div[1]/div[3]/button")
            #delete.click()
            #prefer_not_to_say = self.driver.find_elements_by_xpath("//*[@id='modalOverlay']/div/div/div/div[2]/div/div/div/span[4]/button")
            #prefer_not_to_say.click()
            #self.deleted_ads.append(ad)
            #time.sleep(2)
    
    
    # posts ads
    def post_ad(self, ad, data):
        
        self.next_url("https://www.kijiji.ca/p-select-category.html")
        
        # fills out ad title
        ad_title = self.driver.find_element_by_id("AdTitleForm")
        ad_title.send_keys(data['ad_title'])
        time.sleep(1)
        
        # clicks next, opens up categories
        next = self.driver.find_element_by_xpath("//*[@id='mainPageContent']/div/div/div/div[2]/div/div/div[2]/div[1]/div/button")
        #self.next_click(next)
        next.click()
        time.sleep(3)
        
        # user has the choice to pick the category, or go with suggeted by kijii
        # only works for buy and sell right now
        if data['category'] != "": #if user left it empty
            category_path = data['category'].split(",")
            for cat in category_path:
                #finds the text on the page, then goes one back and clicks the button for the category
                buysell = self.driver.find_element_by_xpath("//button[contains(@class, 'categoryButton')]//*[contains(., '{}')]/..".format(cat)) # buy and sell button
                buysell.click()
                time.sleep(3)
        else:#clicks on the suggested category determined by kijiji
            suggested = self.driver.find_element_by_xpath("//*[@id='CategorySuggestion']/div[1]/ul/li/button")
            self.next_click(suggested)
            time.sleep(2)
            
        self.upload_images() #uploading the pictures, store in the order you want them to be posted
        
        #types in the description
        description = self.driver.find_element_by_name("postAdForm.description")
        description.send_keys(data['description'])
        time.sleep(2)
        
        # set your location
        # ##uncomment this section if you need to change default locations
        ######################################################################################add if wrap###############################################################################
        #change = self.driver.find_element_by_xpath("//*[@id='FESLocationModuleWrapper']/div/div/section/div[2]/div[1]/div[1]/div[2]/button")
        #change.click() #clicks change location button
        #time.sleep(2)
        if self.driver.find_elements_by_id("location"):
            location = self.driver.find_element_by_id("location")
            location.send_keys(data['location'])
            time.sleep(2)
            # select first suggested location
            suggested_location = self.driver.find_element_by_id("LocationSelector-item-0")
            suggested_location.click()
            time.sleep(0.5)        
        
        
        #input price
        price = self.driver.find_element_by_id("PriceAmount")
        price.send_keys(data['price'])
        time.sleep(0.5)
        
        self.optional(data)
        
        time.sleep(10) ######################remove###################################
        
        # posts the ad
        current = self.driver.current_url
        post_ad = self.driver.find_element_by_xpath("//*[@id='MainForm']/div[11]/div/div/button[1]")       
        post_ad.click()
        time.sleep(5)
        if current == self.driver.current_url:
            print('|\n' * 5)
            print('FAILED TO POST AD: {}\n'.format(ad))
            print('|\n' * 5)
            self.failed_postings.append(ad)
            
        else:
            print('|\n' * 5)
            print('KIJIJI AD POSTED SUCCESSFULLY: {}\n'.format(ad))
            print('|\n' * 5)
            self.successfull_postings.append(ad)
    
    
    # takes each image from folder and uploads
    def upload_images(self):
        # kijiji will accept the following file types: jpeg, .jpg, .png, .gif, .bmp
        # uploads all the pictures in the directory
        image = self.driver.find_element_by_xpath("//input[@type='file']") # only has upload button, but this puts it in the hidden filepath
        for file in os.listdir():
            if file.endswith(".jpg" or ".jpeg" or ".png" or ".gif" or ".bmp"):
                image_list = file
                print("posting image: "+image_list) # for user to see
                image.send_keys(os.path.abspath(image_list))# + "\\" + image_list)
                time.sleep(5) # lets the images upload
    
    
    # leave blank in these categories to ignore
    # optional ad information/ other info that may be mandatory
    def optional(self,data):
        
        # if user wants to enter phone number
        try:
            if data['phone'] != "":
                phone = self.driver.find_element_by_name('postAdForm.phoneNumber')
                phone.send_keys(data['phone'])
                time.sleep(0.5)
        except:
            pass
        
        # condition status. condition can either be: New, used-like new, used-good, used-fair 
        try:
            if data['condition'] != "":
                condition = self.driver.find_element_by_id("condition_s")
                condition.click()
                time.sleep(1)
                if data['condition'].lower() == "new":
                    cond = self.driver.find_element_by_xpath("//option[@value='new']")
                    cond.click()
                elif data['condition'].lower() == "usedlikenew":
                    cond = self.driver.find_element_by_xpath("//option[@value='usedlikenew']")
                    cond.click()
                elif data['condition'].lower() == "usedgood":
                    cond = self.driver.find_element_by_xpath("//option[@value='usedgood']")
                    cond.click()
                elif data['condition'].lower() == "usedfair":
                    cond = self.driver.find_element_by_xpath("//option[@value='usedfair']")
                    cond.click()  
        except:
            pass
        
        # optional for tags
        # split tags by a "," and add tags to kijiji
        try:
            if data['tag'] != "":
                tag_list = data['tag'].split(",")
                for tag in tag_list:  
                    tags_input = self.driver.find_element_by_name("postAdForm.tagsInput")
                    tags_input.send_keys(tag)
                    add_tag = self.driver.find_element_by_xpath("//*[@id='MainForm']/div[3]/div/section/div[2]/div[10]/div/div/div/button")
                    add_tag.click()
                    time.sleep(1)
        except:
            pass
        
        # only used for desktop computer, brand name
        try:
            if data['desktop_brand'] != "":
                select_desktop_brand = self.driver.find_element_by_id("desktopbrand_s")
                select_desktop_brand.click()
                time.sleep(1)
                brand = self.driver.find_element_by_xpath("//option[@value='{}']".format(data['desktop_brand']))
                brand.click()
                time.sleep(1)
        except:
            pass
            
        
        # add other options if needed.


if __name__ == "__main__":    
    main = Kijiji(sys.argv)