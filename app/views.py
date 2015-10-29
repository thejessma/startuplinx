from app import app
from flask import url_for, render_template, session, redirect, copy_current_request_context, request, flash, make_response
import json
import random
from sqlalchemy import desc
from collections import OrderedDict

from view_helpers.admin import get_daily_events, get_all_messages
from view_helpers.user import fetch_and_populate_current_user_from_linkedin, \
        get_current_user
from view_helpers.company import feed_companies_query_template, \
        feed_friends_query_template, \
        feed_vetted_companies_query_template, \
        get_companies_and_friends_feed_info_from_query_results, \
        profile_company_query_template, \
        profile_friends_query_template, \
        profile_all_employees_query_template, \
        feed_companies_pending_query_template, \
        kuenne_ceos_and_founders_query_template, \
        get_company_and_friends_profile_info_from_query_results, \
        ADMIN_BASIC_FIELDS, ADMIN_ADVANCED_FIELDS, \
        prepare_companies_for_feed, \
        rescrape_companies_from_list, \
        FROM_URL_RESCRAPE_MODE
from api_helpers.linkedin import get_linkedin_oauth_token, \
        get_linkedin_id, \
        get_current_linkedin_user, \
        linkedin_login, \
        linkedin_logout, \
        kuenne_linkedin_multilogin, \
        LINKEDIN_API_AND_SECRET_KEYS
from models import db, get_datetime, User, Company, Article, Campaign, Recipient, LoggedEvent 
from logging import log_event
from decorators import async, admin_only, gzipped
from forms import model_form
    
@app.route('/')
@gzipped
def index():
    if not get_linkedin_oauth_token():
        log_event(None, 'home', {'ip': request.remote_addr})
        return render_template('home.html')
    if 'user_id' not in session:
        return login_callback()
    return redirect(url_for('feed'))

@app.route('/login')
def login():
    return linkedin_login()

@app.route('/logout')
def logout():
    log_event(session.get('user_id'), 'logout', {'ip': request.remote_addr})
    session.pop('user_id', None)
    session.pop('admin_mode', None)
    linkedin_logout()
    return redirect(url_for('index'))

@app.route('/login_callback')
def login_callback():
    user = get_current_linkedin_user()
    if not user or not user.is_registered:
        return redirect(url_for('register'))
    if not user.last_login:
        show_intro = "intro"
    else:
        show_intro = None
    user.last_login = get_datetime()
    db.session.commit()
    session['user_id'] = user.id
    return redirect(url_for('feed', show_intro=show_intro))

@app.route('/register')
def register():
    print 'DAFUK....'
    @async
    @copy_current_request_context
    def fetch_and_populate_current_user_from_linkedin_async(db):
        fetch_and_populate_current_user_from_linkedin(db)

    # TODO better error handling.. what's the way to do it?
    if 'user_id' in session:
        print 'User already exists and logged in...'
        return redirect(url_for('index'))
    user = get_current_linkedin_user()
    if user and user.is_registered:
        print 'User already exists and is registered...'
        return redirect(url_for('index'))
    if not get_linkedin_oauth_token():
        print 'User not logged in...'
        return redirect(url_for('index'))
    if not user:
        print 'creating hollow user with linkedin_id = ' + str(get_linkedin_id())
        user = User(get_linkedin_id())
        db.session.add(user)
        db.session.commit()

    log_event(session.get('user_id'), 'register', {'ip': request.remote_addr})
    fetch_and_populate_current_user_from_linkedin_async(db)
    print 'FUCKING DONE'
    return render_template('loading.html', current_user=user)

@app.route('/_test_register_page') 
def _test_register_page(): 
    user = get_current_linkedin_user()
    return render_template('loading.html', current_user=user)

# TODO remove
@app.route('/WHATTHEFUCK')
def WHATTHEFUCK():
    return render_template('wtf.html')

@app.route('/feed', defaults={'show_intro': None, 'filter': 'startups'}, methods = ['GET', 'POST'])
@app.route('/feed/<show_intro>', defaults={'filter': 'startups'}, methods=['GET', 'POST'])
@app.route('/feed/<show_intro>/<filter>', methods=['GET', 'POST'])
@gzipped
def feed(show_intro, filter):
    user = get_current_user()
    if not user:
        return redirect(url_for('index'))
    # get feed companies
    feed_companies_query = feed_companies_query_template.format(user.id)
    companies_results = db.engine.execute(feed_companies_query)
    # get feed friends
    feed_friends_query = feed_friends_query_template.format(user.id)
    friends_results = db.engine.execute(feed_friends_query)
    # populate dicts with resulting companies and friends
    companies = get_companies_and_friends_feed_info_from_query_results(companies_results, friends_results)
    # split into 4 vertical columns
    companies_vertical = prepare_companies_for_feed(companies, filter) 
    # pick ahri index
    ahri_column = random.randint(1, 4)
    ahri_row = random.randint(1, len(companies_vertical[0]) / 2 + 1)
    # count how many are still scraping
    feed_companies_pending_query = feed_companies_pending_query_template.format(user.id)
    pending_result = db.engine.execute(feed_companies_pending_query)
    for row in pending_result:
        pending_count = row[0]
    # fetch vetted companies
    exclude_inlist = ",".join([str(id) for id in companies])
    feed_vetted_companies_query = feed_vetted_companies_query_template.format(user.id, exclude_inlist)
    vetted_companies_results = db.engine.execute(feed_vetted_companies_query)
    vetted_companies = get_companies_and_friends_feed_info_from_query_results(vetted_companies_results, [])
    # split into 4 vertical columns
    vetted_companies_vertical = prepare_companies_for_feed(vetted_companies) 
    # log event
    log_event(user.id, 'feed', {'ip': request.remote_addr, 'companies_count': len(companies)})
    # print page
    return render_template('feed.html', companies_vertical=companies_vertical, vetted_companies_vertical=vetted_companies_vertical, pending_count=pending_count, current_user=user, show_intro=show_intro, ahri_column=ahri_column, ahri_row=ahri_row)

@app.route('/profile/<company_id>', methods=['GET', 'POST'])
def profile(company_id):
    user = get_current_user()
    if not user: 
        return redirect(url_for('index'))
    # avoid SQL injections
    company_id = int(company_id)
    # get company
    profile_company_query = profile_company_query_template.format(company_id)
    company_result = db.engine.execute(profile_company_query).fetchone()
    # get friends
    if user.is_admin and session.get('admin_mode'):
        # if admin mode is on, show all employees
        profile_friends_query = profile_all_employees_query_template.format(company_id)
    else:
        # otherwise, just user's friends
        profile_friends_query = profile_friends_query_template.format(user.id, company_id)
    friends_results = db.engine.execute(profile_friends_query)
    # populate dict with resulting company and friends
    company = get_company_and_friends_profile_info_from_query_results(company_result, friends_results)
    if not company:
        return 'ERROR -- no company found'
    log_event(user.id, 'profile', {'ip': request.remote_addr, 'company_id': company['id'], 'company_name': company['name']})
    return render_template('profile.html', company=company, current_user=user)

@app.route('/articles')
def articles():
    articles = Article.query.filter_by(is_visible=True).order_by(Article.order_id, desc(Article.created)).all()
    return render_template('articles.html', articles=articles) 

@app.route('/article/<article_id>')
def article(article_id):
    article = Article.query.get(id=article_id)
    if not article:
        # no such article
        return redirect(url_for('articles'))
    return redirect(article.url)

@app.route('/about')
def about():
    log_event(session.get('user_id'), 'about', {'ip': request.remote_addr})
    return render_template('about.html')

#----------------------------------------------
#              Kuenne's Panel
#----------------------------------------------

def kuenne_get_job_group(job):
    if not job['website_url'] and not job['email_domains_json'] and not job['email']:
        return 'bad'
    if job['title'].lower().find('founder') == -1 and job['title'].lower().find('job') == -1 and job['title'].lower().find('executive') == -1 and job['title'].lower().find('chief') == -1 and job['title'].lower().find('ceo') == -1:
        return 'meh'
    return 'good'

def remove_prefix_if_exists(string, prefix):
    if not string:
        return string
    if string.startswith(prefix):
        return string[len(prefix):]
    return string

def get_stripped_domain(website_url):
    if not website_url:
        return website_url
    prefixes_in_order = ['https://', 'http://', 'http:/', 'www.', 'www3.', 'w3.']
    for prefix in prefixes_in_order:
        website_url = remove_prefix_if_exists(website_url, prefix)
    website_url = website_url.split('/')[0].lower()
    return website_url

def get_job_from_result(result):
    job = dict(result.items())
    job['stripped_website_url'] = get_stripped_domain(job['website_url'])
    return job

def get_top_3_domains(domains):
    top_3 = []
    used = dict()
    for domain in domains:
        if domain and domain not in used:
            top_3.append(domain)
            used[domain] = 1
    return top_3

def permute_emails(first_name, last_name, domains):
    emails = []
    first = first_name.lower()
    last = last_name.lower()
    for domain in domains:
        emails.append(first + '@' + domain)
        emails.append(last + '@' + domain)
        emails.append(first + last + '@' + domain)
        emails.append(first + '.' + last + '@' + domain)
        emails.append(first[0] + last + '@' + domain)
        emails.append(first[0] + '.' + last + '@' + domain)
        emails.append(first + last[0] + '@' + domain)
        emails.append(first[0] + last[0] + '@' + domain)
        emails.append(first[0] + '.' + last[0] + '@' + domain)
        emails.append(first + '_' + last + '@' + domain)
        emails.append(last + first + '@' + domain)
        emails.append(last + '.' + first + '@' + domain)
    return emails

@app.route('/kuenne', defaults={'is_csv': 0}, methods=['GET', 'POST'])
@app.route('/kuenne/<is_csv>', methods = ['GET', 'POST'])
def kuenne(is_csv):
    user = get_current_user()
    if not user.is_admin and user.id != 4973:
        return 'Not Kuenne'
    # first apply any changes to the website url / other form fields
    for field, value in request.form.iteritems():
        if field.startswith('website_') and value:
            print field + ' -> ' + str(value)
            company_id = int(field.split('_')[1])
            company = Company.query.get(company_id)
            print '         setting company_id ' + str(company_id) + ' (' + company.name.encode('utf8') + ') to ' + str(value)
            company.website_url = value
            db.session.commit()

    # then fetch all the CEOs and founders that are connected to Kuenne
    kuenne_query = kuenne_ceos_and_founders_query_template.format(11522) # 11522
    results = db.engine.execute(kuenne_query)
    # split in groups
    groups = OrderedDict({
            'good': [],
            'meh': [],
            'bad': []
    })
    ceos = dict()
    for result in results:
        job = get_job_from_result(result)
        # add job to group
        group = kuenne_get_job_group(job)
        job['group'] = group
        groups[group].append(job)
        # add job to ceo's jobs and potentially fill in fields
        user_id = job['user_id']
        email_domains = json.loads(job['email_domains_json']) if job['email_domains_json'] else []
        if user_id in ceos: 
            ceos[user_id]['jobs'].append(job)
            ceos[user_id]['email_domains'] = [job['stripped_website_url']] + ceos[user_id]['email_domains'] + email_domains
        else:
            ceos[user_id] = {
                'id': user_id,
                'first_name': job['first_name'],
                'last_name': job['last_name'],
                'email': job['email'],
                'group': 'bad',
                'jobs': [job],
                'email_domains': [job['stripped_website_url']] + email_domains,
                'main_email_domains': []
            }
        if group == 'good':
            ceos[user_id]['group'] = 'good'
        # see if that's the position where s/he is CEO and fill the fields
        is_ceo = False
        is_founder = False
        if job['title'].lower().find('founder') != -1:
            is_founder = True
        if job['title'].lower().find('ceo') != -1 or job['title'].lower().find('executive') != -1 or job['title'].lower().find('chief') != -1:
            is_ceo = True
        if is_ceo or is_founder:
            ceos[user_id]['main_email_domains'] = [job['stripped_website_url']] + ceos[user_id]['main_email_domains'] + email_domains
            if is_ceo and is_founder:
                title = 'founder and CEO'
            elif is_ceo:
                title = 'CEO'
            else:
                title = 'founder'
            ceos[user_id]['title'] = title
            ceos[user_id]['company'] = job['company_name']
    # find the good ones by user_id
    good_ids = []
    for job in groups['good']:
        good_ids.append(job['user_id'])
    # split in groups again, this time intelligently
    new_groups = OrderedDict({
            'good': [],
            'meh': [],
            'okay': [],
            'bad': []
    })
    new_group_colors = {
            'good': 'green',
            'meh': 'gray',
            'okay': 'brown',
            'bad': 'red'
    }
    for group, jobs in groups.iteritems():
        if group == 'good':
            new_groups[group] = jobs
        else:
            for job in jobs:
                if job['user_id'] in good_ids:
                    new_groups['okay'].append(job)
                else:
                    new_groups[group].append(job)
    if is_csv:
        # generate CSV file for download
        attributes = ['first_name', 'last_name', 'company', 'title', 'email']
        lines = []
        lines.append(','.join(attributes))
        for id, ceo in ceos.iteritems():
            if ceo['email']:
                # use default email
                line = ','.join(ceo[attr] for attr in attributes)
                lines.append(line)
            else:
                # generate emails from domains and name
                top_3_domains = get_top_3_domains(ceo['main_email_domains'])
                emails = permute_emails(ceo['first_name'], ceo['last_name'], top_3_domains)
                for email in emails:
                    ceo['email'] = email
                    line = ','.join(ceo[attr] for attr in attributes)
                    lines.append(line)
                ceo['email'] = None
        csv = '\n\r'.join(lines)
        response = make_response(csv)
        response.headers["Content-Disposition"] = "attachment; filename=ceos.csv"
        return response
    else:
        return render_template('kuenne.html', current_user=user, groups=new_groups, group_colors=new_group_colors, ceos=ceos)

@app.route('/kuenne_login_callback')
def kuenne_login_callback():
    user = get_current_user()
    if not user.is_admin and user.id != 4973:
        return 'Not Kuenne'
    app_idx = session.get('kuenne_linkedin_app_idx')
    if user.linkedin_tokens_json:
        linkedin_tokens = json.loads(user.linkedin_tokens_json)
    else:
        linkedin_tokens = dict()
    linkedin_tokens[app_idx] = session['kuenne_linkedin_token']
    user.linkedin_tokens_json = json.dumps(linkedin_tokens)
    db.session.commit()
    return redirect(url_for('kuenne_multiaccount'))

@app.route('/kuenne_multiaccount')
def kuenne_multiaccount():
    user = get_current_user()
    if not user.is_admin and user.id != 4973:
        return 'Not Kuenne'
    if user.linkedin_tokens_json:
        linkedin_tokens = json.loads(user.linkedin_tokens_json)
    else:
        linkedin_tokens = dict()
    app_indexes = [str(app_idx) for app_idx in range(len(LINKEDIN_API_AND_SECRET_KEYS))]
    return render_template('kuenne_multiaccount.html', linkedin_tokens=linkedin_tokens, app_indexes=app_indexes, current_user=user)

@app.route('/kuenne_multilogin/<app_idx>')
def kuenne_multilogin(app_idx):
    return kuenne_linkedin_multilogin(app_idx)

@app.route('/list_campaigns')
def list_campaigns():
    user = get_current_user()
    if not user: 
        return redirect(url_for('index'))
    campaigns = Campaign.query.filter_by(user_id=user.id).order_by(desc(Campaign.created)).all()
    return render_template('list_campaigns.html', campaigns=campaigns, current_user=user)

CAMPAIGN_FIELDS = [
    'name',
    'sender_name',
    'sender_email',
    'subject_template',
    'body_template'
]

@app.route('/new_campaign', methods = ['GET', 'POST'])
def new_campaign():
    user = get_current_user()
    if not user: 
        return redirect(url_for('index'))
    CampaignForm = model_form(Campaign, CAMPAIGN_FIELDS)
    campaign = Campaign(user.id)
    form = CampaignForm(request.form, obj=campaign)
    if form.validate_on_submit():
        form.populate_obj(campaign)
        db.session.add(campaign)
        db.session.commit()
        print 'Created new campaign: ' + str(campaign.name)
        return redirect(url_for('list_campaigns'))
    return render_template("new_campaign.html", form=form)

@app.route('/edit_campaign/<campaign_id>', methods = ['GET', 'POST'])
def edit_campaign(campaign_id):
    user = get_current_user()
    if not user: 
        return redirect(url_for('index'))
    CampaignForm = model_form(Campaign, CAMPAIGN_FIELDS)
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return 'No such campaign id' # TODO better
    if campaign.user_id != user.id:
        return 'This is not your campaign' # TODO better
    form = CampaignForm(request.form, obj=campaign)
    if form.validate_on_submit():
        form.populate_obj(campaign)
        db.session.commit()
        print 'Edited campaign id ' + str(campaign.id)
        return redirect(url_for('view_campaign', campaign_id=campaign_id))
    elif form.is_submitted():
        flash(form.errors)
    return render_template("edit_campaign.html", form=form, campaign=campaign)

@app.route('/view_campaign/<campaign_id>')
def view_campaign(campaign_id):
    user = get_current_user()
    if not user: 
        return redirect(url_for('index'))
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return 'No such campaign id' # TODO better
    if campaign.user_id != user.id:
        return 'This is not your campaign' # TODO better
    return render_template('view_campaign.html', campaign=campaign)

#----------------------------------------------
#              Admin Panel
#----------------------------------------------

@app.route('/admin')
@admin_only
def admin():
    current_user = get_current_user()
    users = User.query.filter_by(is_registered=True).order_by(User.name).all()
    return render_template('admin.html', users=users, current_user=current_user)

@app.route('/admin/all_companies')
@admin_only
def admin_all_companies():
    # order by column
    order_by = request.args.get('order_by')
    if not order_by:
        order_by = 'id'
    criterion = getattr(Company, order_by)
    # desc or asc
    order_by_type = request.args.get('type')
    if order_by_type == 'desc':
        criterion = desc(criterion)
    else:
        order_by_type = 'asc'
    # limit
    limit = request.args.get('limit')
    if not limit:
        limit = 25
    else:
        limit = int(float(limit))
    # offset
    offset = request.args.get('offset')
    if not offset:
        offset = 0
    else:
        offset = int(float(offset))
    # search term
    search_term = request.args.get('search_term')
    # get companies
    if search_term:
        companies = Company.query.filter(Company.name.ilike('%' + search_term + '%')).order_by(criterion).limit(limit).offset(offset).all()
    else:
        companies = Company.query.order_by(criterion).limit(limit).offset(offset).all()
    return render_template('admin_all_companies.html', companies=companies, order_by=order_by, order_by_type=order_by_type, limit=limit, offset=offset, search_term=search_term)

@app.route('/admin/edit/<company_id>', defaults={'edit_mode': 'basic'}, methods = ['GET', 'POST'])
@app.route('/admin/edit/<company_id>/<edit_mode>', methods = ['GET', 'POST'])
@admin_only
def admin_edit(company_id, edit_mode):
    if edit_mode == 'advanced':
        fields = ADMIN_ADVANCED_FIELDS
    else:
        fields = ADMIN_BASIC_FIELDS
    CompanyForm = model_form(Company, fields)
    company = Company.query.get(company_id)
    form = CompanyForm(request.form, obj=company)
    if form.validate_on_submit(): 
        form.populate_obj(company)
        db.session.commit()
        print 'Updated ' + str(company.id) + ', ' + company.name.encode('utf8')
        if request.form.get('do_rescrape_from_url'):
            print '     also rescrape!'
            rescrape_companies_from_list([company], mode=FROM_URL_RESCRAPE_MODE)
        return redirect(url_for('profile', company_id=company.id))
    elif form.is_submitted():
        flash(form.errors)
    return render_template("admin_edit.html", fields=fields, form=form, company=company, edit_mode=edit_mode)

@app.route('/admin/add_company_form', methods = ['GET', 'POST'])
@admin_only
def admin_add_company_form():
    return render_template("admin_add_company_form.html")

@app.route('/admin/add_article_form', methods = ['GET', 'POST'])
@admin_only
def admin_add_article_form():
    current_user = get_current_user()
    article_fields = [
        "title",
        "subtitle",
        "url",
        "author_name",
        "image_url",
        "content",
        "mins_to_read",
        "order_id",
        "is_visible"
    ]
    ArticleForm = model_form(Article, article_fields)
    article = Article(current_user.id) 
    form = ArticleForm(request.form, obj=article)
    if form.validate_on_submit(): 
        form.populate_obj(article)
        db.session.add(article)
        db.session.commit()
        print 'Inserted article ' + str(article.title) + ' <--'
        return redirect(url_for('articles'))
    elif form.is_submitted():
        flash(form.errors)
    return render_template("admin_add_article_form.html", fields=article_fields, form=form)

@app.route('/admin/dashboard', methods = ['GET', 'POST'])
@admin_only
def admin_dashboard():
    current_user = get_current_user()
    users = User.query.filter_by(is_registered=True).order_by(User.name).all()
    messages = get_all_messages()
    event_types = ['home', 'register', 'feed', 'profile', 'send_message', 'about', 'logout']
    daily_events = {t: get_daily_events(t) for t in event_types}
    return render_template("admin_dashboard.html", users=users, current_user=current_user, messages=messages, daily_events=daily_events)

@app.route('/admin/messages', methods = ['GET', 'POST'])
@admin_only
def admin_messages():
    messages = get_all_messages()
    return render_template("admin_messages.html", messages=messages)
