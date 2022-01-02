# Kijiji-reposter
Python program that can post kijiji ads, delete them, and gather statistics on the ads.

Setup
- python3
- Run pip3 install -r requirements.txt to install all dependencies
- To download chromedriver go to: https://chromedriver.chromium.org/downloads. Make sure to put chromedriver.exe in the main directory as shown below.


__Structure__

    |-rootdir
        |
        |--kijiji-poster.py
        |--login-info.json
        |--requirements.txt
        |--chromedriver.exe
        |--README
        |--kijiji_ads
            |
            |-example_1
            |-example_2
            |...
            |-example_x
                |
                |-example_x_ad_info.json
                |-image1
                |-image2
                |...
                |-imagex
                
__notes__

    notes: kijiji may have a captcha, user should manually fill out captch to proceed.
    notes: random user agents may provide an outdated browser without a captcha. you will need to re-run the program.
    notes: each folder in kijiji_ads will include a .json file for the ad information and all the images for the given ad. the images will be posted in chronological order.
    json: json is located in the folder for the ad with the images for the given ad.
    login-info.json will store your username and password for your account.
    image: please include at least one image. images must be located in the folder with the json file for the ad.
    image: there may be a specific image size, so make sure your image is not too large or too small

__ads - ####.json format:__

    {
        "ad_title":"",      #--> ad title: must be minimmum 8+ characters long
        "description":"",   #--> description: must be minimmum 10+ characters long
        "category":"",      #--> category to be posted in. if left blank, will use suggested category. Otherwise, follow the order in which the categories should ...
                            #... be selected. ex. to post in speakers -> "Buy & Sell,Audio,Speakers". do not include any spaces after comma and write it as it appears on kijiji.
        "location":"",      #--> location. use postal code. can use just the first half of postal code: ex. "l4y" or the whole thing: ex. "l4y 2r5"
        "price":"",         #--> price of product. ex "199"
        "phone":"",         #--> optional phone number. ex "1112223333" leave blank if not applicable: ex. ""
        "tag":"",           #--> optional tags for the ad. write in comma seperated list. ex. "desktop, pc, computer, gaming" leave blank if not applicable. You must add a space after the tag to indicate an input
        "condition":"",     #--> optional condition of item. can be the following: "new", "usedlikenew", "usedgood", "usedfair" leave blank if not applicable.
        "desktop_brand":""  #--> look at the brand options. write as "desktop<brand>" ex. "desktopcustom" or "desktopacer" leave blank if not applicable.
    }

__login-info.json - format:__

    {
        "username":"", #--> your username or email
        "password":""  #--> your password
    }


user prompts:

    "post all": posts all ads in directory
    "delete all": deletes all ads in directory from kijiji
    "delete and post" combination of deleting and reposting the ads from the folders on kijiji
    "<ad_file>": just enter the name of the file you want to post by itself
    "f" or "exit" or "end": finishes the script and returns results
    also takes command line arguments. just type the command after the main kijiji.py 

self.max_page: max page to delete ad

self.max_replies: max number of replies to delete ad

self.attempts: attempts when running from the command line
