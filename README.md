# Item Catalog Application

This is a Project Management application which provides a list of projects within a variety of countries as well as provide a user registration and authentication system. 
Registered users will have the ability to post, edit and delete their own ProjectItems.

### Prerequisites

   - Install [VirtualBox](https://www.virtualbox.org/)
   - Install [Vagrant](https://www.vagrantup.com/)
   - Download the vagrant setup files from [Udacity's Github](https://github.com/udacity/fullstack-nanodegree-vm)
     These files configure the virtual machine and install all the tools needed to run this project.
   - Download the ProjectManagement.zip ,unzip it and put it inside the vagrant directory.
   
### How to Run
  
  Please ensure you have Python, Vagrant and VirtualBox installed. This project uses a pre-congfigured Vagrant virtual machine which has the Flask server installed 
   
   - $ vagrant up
   - $ vagrant ssh
   - $ cd /vagrant
   - $ cd /ProjectManagement
   - $ python project.py
   - access application on 'http://localhost:5000'

### JSON EndPoints:

  - http://localhost:5000/country/JSON
  
  <img src="screenshots/countriesJSON.png" width="800">
  
  - http://localhost:5000/country/1/project/JSON
  
  <img src="screenshots/oneCountryJSON.png" width="800">
  
  - http://localhost:5000/country/1/project/1/JSON
  
  <img src="screenshots/oneProjectJSON.png" width="800">
  
### ScreenShots:
   
  - please find screenshots in folder having name screenshots  
  

# Creator

**Radhika Rathore**



