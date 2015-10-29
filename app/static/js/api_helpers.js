var SERVER_URL = window.location.origin

function pingMeWhenUserRegisters(linkedin_id) { // linkedin_id not used TODO remove
    console.log('wait for register call');
    $.ajax({
        'url' : SERVER_URL + '/wait_for_register',
        'type' : 'GET',
        'dataType' : 'json',
        'timeout': 0, // in milliseconds; 0 for unlimited
        'data' : {
        },
        'success' : onUserRegisteredSuccessfully,
        'error' : genericError
    });
}

// NEVER EVER EVER EVER CALL THESE from a link or button within a form...
// http://stackoverflow.com/questions/10906604/ajax-request-not-working-in-safari-chrome
// http://bartwullems.blogspot.com/2012/02/ajax-request-returns-status-0.html
function sendLinkedinMessage(friend_id, form_id) {
    subject = $('#' + form_id).find('[name=subject]').val();
    body = $('#' + form_id).find('[name=body]').val();
   // console.log('subject' + subject)
   // console.log('body: ' + body)
    $.ajax({
        'url' : SERVER_URL + '/send_linkedin_message/' + friend_id,
        'contentType': "application/json; charset=utf-8",
        'type': "POST",
        'dataType' : 'json',
        'data': JSON.stringify({
            'subject': subject,
            'body': body
        }),
        'success': onSendLinkedinMessageSuccess,
        'error': genericModalError
    });
}

// NEVER EVER EVER EVER CALL THESE from a link or button within a form...
// http://stackoverflow.com/questions/10906604/ajax-request-not-working-in-safari-chrome
// http://bartwullems.blogspot.com/2012/02/ajax-request-returns-status-0.html
function sendFeedback(form_id) {
    url = document.URL;
    text = $('#' + form_id).find('[name=text]').val();
   // console.log('subject' + subject)
   // console.log('body: ' + body)
    $.ajax({
        'url' : SERVER_URL + '/send_feedback',
        'contentType': "application/json; charset=utf-8",
        'type': "POST",
        'dataType' : 'json',
        'data': JSON.stringify({
            'url': url,
            'text': text
        }),
        'success': onSendFeedbackSuccess,
        'error': genericModalError
    });
}

function addFavorite(company_id) {
    $.ajax({
        'url' : SERVER_URL + '/add_favorite/' + company_id,
        'contentType': "application/json; charset=utf-8",
        'type' : 'GET',
        'dataType' : 'json',
        'data' : {
        },
        'success' : onAddFavoriteSuccess,
        'error' : genericError
    });
}

function removeFavorite(company_id) {
    $.ajax({
        'url' : SERVER_URL + '/remove_favorite/' + company_id,
        'contentType': "application/json; charset=utf-8",
        'type' : 'GET',
        'dataType' : 'json',
        'data' : {
        },
        'success' : onRemoveFavoriteSuccess,
        'error' : genericError
    });
}

function onRemoveFavoriteSuccess(data, textStatus, jqXHR) {
    company_id = data['company_id'];
    wrapper_id = "company_wrapper_" + company_id;
    jQuery($('#' + wrapper_id).find(".favorite")[0]).show();
    jQuery($('#' + wrapper_id).find(".unfavorite")[0]).hide();
    jQuery($('#' + wrapper_id).find(".is_favorited")[0]).val(0);
}

function onAddFavoriteSuccess(data, textStatus, jqXHR) {
    company_id = data['company_id'];
    wrapper_id = "company_wrapper_" + company_id;
    jQuery($('#' + wrapper_id).find(".favorite")[0]).hide();
    jQuery($('#' + wrapper_id).find(".unfavorite")[0]).show();
    jQuery($('#' + wrapper_id).find(".is_favorited")[0]).val(1);
}

function onUserRegisteredSuccessfully(data, textStatus, jqXHR) {
    window.location.reload();
}

function onSendLinkedinMessageSuccess(data, textStatus, jqXHR) {
    status = data['status'];
    if (status != 'ok') {
        alert('For whatever reason LinkedIn is not accepting the message... We recommend logging into LinkedIn and sending it from there instead. Apologies for the inconvenience!');
    }
    else {
        alert('Message sent successfully!');
    }
    location.href = '#close';
}

function onSendFeedbackSuccess(data, textStatus, jqXHR) {
    status = data['status'];
    if (status != 'ok') {
        alert('Oops! Something is off on our end. Please try sending e-mailing instead. Your opinion matters a lot to us!');
    }
    else {
        alert('Thanks for your feedback! We really appreciate it and will take it into consideration.');
    }
    location.href = '#close';
}

function genericError(jqXHR, textStatus, errorThrown) {
    alert("Oops! Something went wrong... our bad! We will look into it asap.");
    console.log(jqXHR);
    console.log(textStatus);
    console.log(errorThrown);
    console.trace();
}

function genericModalError(jqXHR, textStatus, errorThrown) {
    alert("Oops! Something went wrong... our bad! We will look into it asap.");
    console.log(jqXHR);
    console.log(textStatus);
    console.log(errorThrown);
    console.trace();
    location.reload();
}

$(document).ready(function() {
});
