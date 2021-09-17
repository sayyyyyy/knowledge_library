# Knowledge Library

## Site
http://knowledge-library.azurewebsites.net/
通知機能は省いてあります

## VIDEO DEMO
https://www.youtube.com/watch?v=iEbx33zeabA

## Producer
College students living in Japan

## SKILLS
- html
- css
    - bootstrap
- javascript
    - jquery
- python
    - flask
- git
    - github
- SQL
    - sqlite

## TARGET PERSON
People who study hard

## Why I MADE IT
The background to creating this project can be tedious to search the same page over and over while researching. In addition, there are sites where you cannot tell at a glance what you have searched for in bookmarks. We have developed this web app to solve these problems.

## DESCRIPTION
This project is an application that allows you to save and search URLs, titles, comments, etc. on the site, and is an extended version of bookmarks.

## FUNCTION
- Login function
- Ability to add and display a list by entering a URL and tag
- Ability to add and display pages by entering titles, urls and comments
- Ability to search list tags and see other people's lists
- Ability to send notifications in a few days so you don't forget pages you searched for in the past
    - Decide whether to notify when creating a page and send a notification only to the checked page

# FUNCTION TO BE ADDED IN THE FUTURE
- Changes to google chrome extensions
- Use voice input when searching
- Don't get any more notifications without clicking the notification a few times
- E-mail will be treated as junk e-mail, so I want to avoid it

## DATABASE
- User table
    - id    : this is user id
    - name  : this is username
    - email : this is user's email adress
    - password  : this is user's password,
    - change_pass: if user want to change password, become 1
    - time  : time when the user was created
- List table
    - id    : this is list id
    - tag   : this is tags to attach to the list
    - list_title :this is list title
    - user_id : this is id of user who created the list
- Page table
    - id    : this is page id
    - tag   : this is tags to attach to the page
    - url   : this is url of the page
    - page_title    : this is page title
    - comment : this is comment of page
    - notification : if user want to notice, become 1
    - time  : time when page was created
    - user_id : this is id of user who created the list
    - list_id : this is id of the list that contains this page

## PAGE
- User register Page
    - Page where users can be registered
- Login Page
    - Pages where you can log in
- Logout Page
    - Pages where you can log out
- Lost password Page
    - page that prompts for an email address and sends an email if the user forgets the password
- Change password Page
    - Page where you can change your password
- Main Page(List display)
    - Page can show ther list that the user has and can search the list with the specified tag
- Page display Page
    - Page can see the pages in the specified list
- Search Page
    - Page can see the list searched on the main page
- Add list Page
    - Page can add a list
- Add page Page
    - Page can add a page
