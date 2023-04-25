var FormValidation = 'FormValidation' || {};
"use strict"
FormValidation = {
	init:function(){
		var _this = this;
		_this.constatns = api_constants.init();
		_this.bindEvents();
	},
	bindEvents : function(){
		var _this = this;
		$('body').on('blur focus keyup','form input:text , form input:password , form input[type=email] , form input[type=tel], form textarea ' ,_this.formValidation);
		$('body').on('click','form input:checkbox, form input:radio',_this.formValidation);
		$('body').on('change focus','select',_this.formValidation);
		$('body').on('click','form button', function(event){_this.submitForm($(this).closest('form').attr('name')); });
	},
	formValidation : function(event){
		var isItRequiredField = $(this).prop("required"),
        elemId = $(this).prop("id"),
        elemVal = $(this).val();
        if(!elemVal && isItRequiredField){
        	FormValidation.isEmptyField(elemId,event.type);
        }else if(elemId =='day' || elemId == 'month' || elemId == 'year' ){
        	FormValidation.validateDOB();
        }else if(elemId =='state' || elemId == 'country'){
        	FormValidation.validateSelectBox(elemId);
        }else if(elemId === 'fullname' && $(this).prop("type") === 'text'){
        	if($("#"+elemId).value != ''){
        		$('button.continue').removeClass('disable-button');
        		$('button.continue').removeAttr('disabled');
        	}else{
        		$('button.continue').addClass('disable-button');
        	}
        }else if(elemVal && elemId !== 'termsAndCond'){
        	$('#'+elemId).next('p.error').remove();
        	$('#'+elemId).removeClass('error-border');
        }
	},
	isEmptyField : function(elemId,eventType){
		if(eventType == 'focusin'){
			$('#'+elemId).removeClass('error-border');
		}else{
			$('#'+elemId).addClass('error-border');
			if(elemId == 'month' || elemId == 'day' || elemId == 'year'){
				var day = $('#day :selected').val(),
					month = $('#month :selected').val(),
					year = $('#year :selected').val();
					if(day === '' || month === '' || year === ''){
						$("p#dob-error").text(FormValidation.constatns.errorMsg['dob'].emptyMsg).addClass('error');
					}
			}else if(elemId == 'state' || elemId == 'country'){
				$("p#"+elemId+"-error").text(FormValidation.constatns.errorMsg[elemId].emptyMsg).addClass('error');
			}else if($('#'+elemId).next('p.error').length==0){
				$("#"+elemId).after("<p class='error'>"+ FormValidation.constatns.errorMsg[elemId].emptyMsg+"</p>");
			}
		}
	},
	submitForm : function(formName){
		var validatedFormClass = $('.'+formName);
	    $('.form-field:visible',validatedFormClass).each(function(index) {
	        var isItRequiredField = $(this).prop("required"),
	        elemId = $(this).prop("id"),
	        optional = $(this).attr("data-optional"),
	        elemVal = $(this).val();
	        if(!elemVal && isItRequiredField){
	        	FormValidation.isEmptyField(elemId);
	        }
	        else if(isItRequiredField || optional === 'req'){
	        	FormValidation.validateEachField(elemId,elemVal);
	        }else if(isItRequiredField || optional === 'opt'){
	        	FormValidation.validateEachField(elemId,elemVal,optional);
	        }
	    });
	    if($('.'+formName).find('.error-border').length == 0){
	    	$('.'+formName).submit();
	    }
	},
	validateEachField : function(elemId, elemVal,optional) {
	    var _this = this;
	    switch (elemId) {
	        case "phone": case "zipcode": case "email":
	        	if(optional === 'opt'){
	        		if(elemVal){
	        			return _this.validateWithReg(elemId,elemVal);
	        		}
	        	}else{
	        		return _this.validateWithReg(elemId,elemVal);
	        	}
	            break;
	        case "reTypeEmail":
	        	if(optional === 'opt'){
	        		if(elemVal){
	        			return _this.reTypeFieldValidaton('email',elemId,elemVal);
	        		}
	        	}else{
	        		return _this.reTypeFieldValidaton('email',elemId,elemVal);
	        	}
	            break;
	        case "retypeUserName":
	        	return _this.reTypeFieldValidaton('userName',elemId,elemVal);
	            break;
	        case "reTypePwd":
	        	return _this.reTypeFieldValidaton('password',elemId,elemVal);
	            break;
	        case "reTypePwd1":
	        	return _this.reTypeFieldValidaton('password',elemId,elemVal);
	            break;
	        case "reTypePwd2":
	        	return _this.reTypeFieldValidaton('password',elemId,elemVal);
	            break;
	        case "reTypePwd3":
	        	return _this.reTypeFieldValidaton('password',elemId,elemVal);
	            break;
            case "reTypePwd4":
	        	return _this.reTypeFieldValidaton('password',elemId,elemVal);
	            break;
	    }
	},
	minLength : function(elemId,elemVal){
		console.log(elemVal);
	},
	maximumLength : function(elemId,elemVal){
		console.log(elemVal);
	},
	validateWithReg : function(elemId,elemVal){
		var flag = FormValidation.constatns.errorReg[elemId].test(elemVal);
		FormValidation.addOrRemoveErrorMsg(elemId,flag);
	},
	reTypeFieldValidaton : function(id,retypeId,elemVal){
		var fieldVal = $('#'+id).val(),
		    flag;
		    if(id === 'password' || id === 'userName'){
		    	flag = fieldVal ? 'true' : 'false';
		    }else{
		    	flag = FormValidation.constatns.errorReg[id].test(fieldVal);
		    }
		if(flag){
			if(FormValidation.compareTwoStrings(fieldVal,elemVal)){
				FormValidation.addOrRemoveErrorMsg(retypeId,flag);
			}else{
				FormValidation.addOrRemoveErrorMsg(retypeId,!flag);
			}
		}
	},
	addOrRemoveErrorMsg:function(elemId,flag){
		if(!flag){
			$('#'+elemId).addClass('error-border');
			if($('#'+elemId).next('p.error').length==0){
				$("#"+elemId).after("<p class='error'>"+ FormValidation.constatns.errorMsg[elemId][elemId]+"</p>");
			}
		}else{
			$('#'+elemId).removeClass('error-border');
		}
	},
	compareTwoStrings: function(str1,str2){
		if( str1 === str2 ){
			return true;
		}else{
			return false;
		}
	},
	validateDOB: function()  {
		var day = $('#day :selected').val(),
			month = $('#month :selected').val(),
			year = $('#year :selected').val();
			if(day.length>0 && month.length>0 && year.length>0){
				$("p#dob-error").removeClass('error').text('');
			}
	},
	validateSelectBox: function(elemId){
		var selectedValue = $('#'+elemId+' :selected').val();
		if(selectedValue.length>0){
				$("p#"+elemId+"-error").removeClass('error').text('');
		}
	}
};
(function(){
	if($('.main-container form').length>0){
		FormValidation.init();
	}
})(jQuery)