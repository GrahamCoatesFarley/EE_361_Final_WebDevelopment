# Soteria - Keystroke Dynamics MFA Website

This website demonstrates keystroke dynamics as an alternative MFA other than the popular OTP or push notification MFAs.

## Prerequisite
This application requires [Docker](https://www.docker.com/) to be installed in your computer.

## House Keeping

1. Create a copy of the file `.env_sample` and give it the name `.env`
2. Visit [SendGrid](https://sendgrid.com) to create an account for sending email.
3. Follow the guide [here](https://app.sendgrid.com/guide/integrate/langs/smtp) on how to set up a new API key.
4. Enter the SendGrid API key and account email as `SENDGRID_EMAIL_ADDRESS`, `SENDGRID_API_KEY` respectively in your `.env` file.
5. Visit [Twilio](https://twilio.com) and create an account to get an assigned phone number for sending SMS.
6. Enter the Twilio Account SID, Auth Token and Phone Number as `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`,`TWILIO_PHONE_NUMBER` respectively in your `.env` file.

House is clean!

## Installation

This project already comes with a `docker-compose.yml` file.
All you have to do you is to build the images and run containers using the command below: 

```bash
docker-compose up --build
```

You should be able to access the web page on your browser using:

```bash
http://localhost:8000
```

<img src="home_screen.png" align="center">

## Usage

Steps to follow for a successful interaction with the website.

1. Complete Signup.
2. Login.
3. Attempt account recovery (forgot password)

#### NOTE: First 4 logins or account recoveries use OTP as MFA, after which keystroke dynamics is used.


## Credit

This project is forked from the repository [https://github.com/wahabaa/keystroke-web-MFA](https://github.com/wahabaa/keystroke-web-MFA)
Originally developed by 
<div style="display:flex;align-items:center;">
    <img src="img_1.png" align="left">
   <div style="margin-left:10px;margin-right:20px;">
   <h4> Ahmed Anu Wahab <br> </h4>

[ahmedanuwahab@gmail.com](ahmedanuwahab@gmail.com) <br>
[wahabaa@clarkson.edu](wahabaa@clarkson.edu)

   </div>
</div>

[SERL Clarkson, CITER](https://clarkson.edu)