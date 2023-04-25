var api_constants = 'api_constants' || {};
"use strict";
api_constants = {
	init: function(){
		var constantObject = {
			errorMsg:{
				userName:{
					emptyMsg:'User Name is needed to continue'
				},
				password:{
					emptyMsg:'Password is needed to continue'
				},
				memberId:{
					emptyMsg:'Member ID is needed to continue'
				},
				fullFname:{
					emptyMsg:'First name is needed to continue'
				},
				fullname:{
					emptyMsg:'You must sign with your full name to continue'
				},
				fullLname:{
					emptyMsg:'Last name is needed to continue'
				},
				month:{
					emptyMsg:'Month is needed to continue'
				},
				day:{
					emptyMsg:'Day is needed to continue'
				},
				year:{
					emptyMsg:'Year is needed to continue'
				},
				dob:{
					emptyMsg:'Date of Birth is needed to continue'
				},
				zipcode:{
					emptyMsg:'ZIP Code is needed to continue',
					zipcode: 'Zip Code must be a 5 digit number'
				},
				email:{
					emptyMsg:'Email is needed to continue',
					email: 'Please enter valid email address'
				},
				retypeUserName:{
					emptyMsg:'Re-Type Username is needed to continue',
					retypeUserName: 'Username and Re-Type Username must be the same'
				},
				reTypeEmail:{
					emptyMsg:'Re-Type Email is needed to continue',
					reTypeEmail: 'Email and Re-Type Email both should be same'
				},
				reTypePwd:{
					emptyMsg:'Retype Password is needed to continue',
					reTypePwd: 'Password and Re-Type Password both should be same'
				},
				reTypePwd1:{
					emptyMsg:'Retype Password is needed to continue',
					reTypePwd: 'Password and Re-Type Password both should be same'
				},
				reTypePwd2:{
					emptyMsg:'Retype Password is needed to continue',
					reTypePwd: 'Password and Re-Type Password both should be same'
				},
				reTypePwd3:{
					emptyMsg:'Retype Password is needed to continue',
					reTypePwd: 'Password and Re-Type Password both should be same'
				},
				reTypePwd4:{
					emptyMsg:'Retype Password is needed to continue',
					reTypePwd: 'Password and Re-Type Password both should be same'
				},
				question:{
					emptyMsg:'Question is needed to continue'
				},
				answer:{
					emptyMsg:'Answer is needed to continue'
				},
				address:{
					emptyMsg:'Address is needed to continue'
				},
				city:{
					emptyMsg:'City is needed to continue'
				},
				state:{
					emptyMsg:'State is needed to continue'
				},
				country:{
					emptyMsg:'Country is needed to continue'
				},
				declaretext:{
					emptyMsg:'Declare text is needed to continue'
				},
				phone:{
					emptyMsg:'Phone number  is needed to continue',
					phone:'Please enter valid phone number like (555) 555-5555'
				}
			},
			errorReg:{
				empty:/^\s*$/,
				// zipcodeReg:/^([a-zA-Z0-9_-]){3,5}$/,
				zipcode:/^\d{5}$/,
				email:/^\w+[\w-\.]*\@\w+((-\w+)|(\w*))\.[a-z]{2,3}$/,
				phone:/^[\+]?[(]?[0-9]{3}[)]?[-\s]?[0-9]{3}[-\s]?[0-9]{4,6}$/
				//(123) 456-7890 , (123)456-7890 , 123-456-7890 , 1234567890 , +31636363634 ,075-63546725
				//phone:/^(\()?\d{3}(\))?(-|\s)?\d{3}(-|\s)\d{4}$/ 
			}
		}
		return constantObject;
	}
};
