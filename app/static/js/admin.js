var SERVER_URL = window.location.origin

function createDatabase() { 
    if (confirm('This will call db.create_all(). Are you sure you want to continue?')) {
        $.ajax({
            'url' : SERVER_URL + '/admin/create_db',
            'type' : 'GET',
            'dataType' : 'json',
            'data' : {
            },
            'success' : onCreateDatabaseSuccess,
            'error' : genericError
        });
    } else {
    }
}

function rescrapeAllCompanies() {
    if (confirm('This will send all companies that have crunchbase_data == NULL to the scraper for rescraping. Are you sure you want to continue?')) {
        $.ajax({
            'url' : SERVER_URL + '/admin/rescrape_all_companies',
            'type' : 'GET',
            'dataType' : 'json',
            'data' : {
            },
            'success' : onRescrapeAllCompaniesSuccess,
            'error' : genericError
        });
    } else {
    }
}

function rescrapeAllCompaniesFromUrl() {
    if (confirm('This will send all companies that have a crunchbase_url to the scraper for rescraping. It will also update the crunchbase_urls on the remote. Are you sure you want to continue?')) {
        $.ajax({
            'url' : SERVER_URL + '/admin/rescrape_all_companies/from_url',
            'type' : 'GET',
            'dataType' : 'json',
            'data' : {
            },
            'success' : onRescrapeAllCompaniesSuccess,
            'error' : genericError
        });
    } else {
    }
}

function softRescrapeAllCompanies() {
    if (confirm('This will send all companies for soft rescraping, i.e. only some fields will be refreshed and only using the stored crunchbase_data (i.e. no API calls will be made; however, we will sync up everybody with the remote). Are you sure you want to continue?')) {
        $.ajax({
            'url' : SERVER_URL + '/admin/rescrape_all_companies/soft',
            'type' : 'GET',
            'dataType' : 'json',
            'data' : {
            },
            'success' : onRescrapeAllCompaniesSuccess,
            'error' : genericError
        });
    } else {
    }
}

function rescrapeAllUserImages() {
    if (confirm('This will send all user images where picture_url is not NULL but the local_picture_url is NULL for scraping -- they will be stored in Dropbox and the local_picture_url\'s made to point to that. Are you sure you want to continue?')) {
        $.ajax({
            'url' : SERVER_URL + '/admin/rescrape_all_user_images',
            'type' : 'GET',
            'dataType' : 'json',
            'data' : {
            },
            'success' : onRescrapeAllUserImagesSuccess,
            'error' : genericError
        });
    } else {
    }
}

function loginAsUser() { 
    new_user_id = $('#login_as_users option:selected').val();
    new_user_name = $('#login_as_users option:selected').html();
    console.log(new_user_name);
    console.log(new_user_id);
    if (confirm('You will switch to the user ' + new_user_name + '. The session linkedin_id and user_id will change but the session oauth token will not. Are you sure you want to continue?')) {
        document.location.href = '/admin/login_as/' + new_user_id;
    } else {
    }
}

function toggleAdminMode() {
    if (confirm('This will toggle admin mode. When in admin mode, you will see extra buttons on the regular website that will allow you to change things dynamically. Are you sure you want to continue?')) {
        document.location.href = '/admin/toggle_admin_mode';
    } else {
    }
}

// Make sure the button is outside of the form!
function addCompany() {
    company_linkedin_id = $('#new_company_form').find('[name=company_linkedin_id]').val();
    company_name = $('#new_company_form').find('[name=company_name]').val();
    company_crunchbase_url = $('#new_company_form').find('[name=company_crunchbase_url]').val();
    // noramlize fields
    if (!company_linkedin_id) {
        company_linkedin_id = "";
    } else {
        company_linkedin_id = company_linkedin_id.trim();
    }
    if (!company_name) {
        company_name = "";
    } else {
        company_name = company_name.trim();
    }
    if (!company_crunchbase_url) {
        company_crunchbase_url = ""
    } else {
        company_crunchbase_url = company_crunchbase_url.trim();
    }
    // verify fields and alert user
    if (company_linkedin_id.length == 0) {
        if (!confirm("The linkedin id is empty. We will add a fake linkedin id instead. When real employees of this company log in, this will create a duplicate profile and you'll have to merge them. We recommend going to linkedin and looking up the company and pasting in its linkedin id. Are you sure you want to continue?")) {
            return;
        }
    }
    if (company_crunchbase_url.length == 0) {
        if (!confirm("The crunchbase url is empty. We will attempt to find company by name instead, however we strongly recommend looking it up on crunchase and pasting the correct link here.")) {
            return;
        }
    }
    if (company_name.length == 0) {
        alert("The company name cannot be empty. Especially if there is no crunchbase url b/c then we look up the company by name."); 
        return;
    }
    // send form
    $.ajax({
        'url' : SERVER_URL + '/admin/add_company',
        'contentType': "application/json; charset=utf-8",
        'type': "POST",
        'dataType' : 'json',
        'timeout': 0, // in milliseconds; 0 for unlimited
        'data': JSON.stringify({
            'name': company_name,
            'linkedin_id': company_linkedin_id,
            'crunchbase_url': company_crunchbase_url
        }),
        'success': onAddCompanySuccess,
        'error': onAddCompanyError 
    });
    $('#add_company').hide();
    $('#waiting').show();
}

function mergeCompaniesDialog() {
    $('#mother_company').empty();
    selected_count = 0;
    $('input:checked').each(function () {
        var company_id = (this.checked ? $(this).val() : "");
        selected_count++;
        $('#mother_company')
            .append($("<option></option>")
            .attr("value", company_id)
            .text(companies[company_id]));
    });
    if (selected_count > 1) {
        location.href='#openModal_mergeCompanies';
    } else {
        alert('You must select at least two companies to merge.');
    }
}

function mergeCompanies() {
    mother_company_id = $('#mother_company option:selected').val();
    merge_company_ids = new Array();
    $('input:checked').each(function () {
        var company_id = (this.checked ? $(this).val() : "");
        if (company_id != mother_company_id) {
            merge_company_ids.push(company_id);
        }
    });
    $.ajax({
        'url' : SERVER_URL + '/admin/merge_companies',
        'contentType': "application/json; charset=utf-8",
        'type': "POST",
        'dataType' : 'json',
        'timeout': 0, // in milliseconds; 0 for unlimited
        'data': JSON.stringify({
            'mother_company_id': mother_company_id,
            'merge_company_ids': merge_company_ids 
        }),
        'success': onMergeCompaniesSuccess,
        'error': onMergeCompaniesError
    });
}

function rescrapeList() {
    if (confirm('This will rescrape selected companies from crunchbase. Are you sure you want to continue?')) {
        company_ids = new Array();
        $('input:checked').each(function () {
            var company_id = (this.checked ? $(this).val() : "");
            company_ids.push(company_id);
        });
        $.ajax({
            'url' : SERVER_URL + '/admin/rescrape_select_companies',
            'contentType': "application/json; charset=utf-8",
            'type' : 'POST',
            'dataType' : 'json',
            'data' : JSON.stringify({
                'company_ids': company_ids
            }),
            'success' : onRescrapeListSuccess,
            'error' : genericError
        });
    } else {
    }
}

function softRescrapeList() {
    if (confirm('This will soft rescrape selected companies. This means that only the fields from crunchbase_data will be recomputed; nothing will be fetched from actual crunchbase. Are you sure you want to continue?')) {
        company_ids = new Array();
        $('input:checked').each(function () {
            var company_id = (this.checked ? $(this).val() : "");
            company_ids.push(company_id);
        });
        $.ajax({
            'url' : SERVER_URL + '/admin/rescrape_select_companies/soft',
            'contentType': "application/json; charset=utf-8",
            'type' : 'POST',
            'dataType' : 'json',
            'data' : JSON.stringify({
                'company_ids': company_ids
            }),
            'success' : onSoftRescrapeListSuccess,
            'error' : genericError
        });
    } else {
    }
}

function onRescrapeAllUserImagesSuccess() {
    alert("User images sent for rescraping successfully!");
}

function onSoftRescrapeListSuccess(data, textStatus, jqXHR) {
    status = data['status'];
    if (status != 'ok') {
        alert('Something messed up -- didn\'t get OK from server.');
    } else {
        alert('Companies sent for soft rescraping successfully!');
    }
}

function onRescrapeListSuccess(data, textStatus, jqXHR) {
    status = data['status'];
    if (status != 'ok') {
        alert('Something messed up -- didn\'t get OK from server.');
    } else {
        alert('Companies sent for rescraping successfully!');
    }
}

function onMergeCompaniesSuccess(data, textStatus, jqXHR) {
    status = data['status'];
    if (status != 'ok') {
        onMergeCompaniesError();
    } else {
        alert('Companies merged successfully!');
        company_id = data['company_id']
        document.location.href = '/profile/' + company_id;
    }
}

function onMergeCompaniesError() {
    alert('SHIT! Something fucked up...');
    location.href = "#close"
}

function onAddCompanySuccess(data, textStatus, jqXHR) {
    status = data['status'];
    if (status != 'ok') {
        onAddCompanyError();
    }
    else {
        alert('Company added successfully!');
        company_id = data['company_id']
        document.location.href = '/profile/' + company_id;
    }
}

function onAddCompanyError() {
    alert('SHIT! Something fucked up...');
    $('#add_company').show();
    $('#waiting').hide();
}

function onCreateDatabaseSuccess() {
    alert("Database created successfully!");
}

function onRescrapeAllCompaniesSuccess() {
    alert("Companies sent for rescraping successfully!");
}

function onLoginAsUserSuccess() {
    location.href='#YOHOO';
}

function genericError(jqXHR, textStatus, errorThrown) {
    alert("Something went wrong... our bad! We will look into it asap.");
    console.log(jqXHR);
    console.log(textStatus);
    console.log(errorThrown);
    console.trace();
}
