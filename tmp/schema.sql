CREATE TABLE companies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified TIMESTAMP NOT NULL,
    name VARCHAR(64) UNIQUE,
    logo_url VARCHAR(256),
    funding_amount BIGINT,
    funding_series VARCHAR(32),
    offices VARCHAR(256),
    headquarters VARCHAR(256),
    founded_year INT,
    investors VARCHAR(1024),
    leadership VARCHAR(1024),
    employees_min INT,
    employees_max INT,
    motto VARCHAR(256),
    summary TEXT,
    industry VARCHAR(256),
    rating_glassdoor FLOAT,
    website_url VARCHAR(256),
    glassdoor_url VARCHAR(256),
    crunchbase_url VARCHAR(256),
    angellist_url VARCHAR(256),
    facebook_url VARCHAR(256),
    linkedin_url VARCHAR(256),
    twitter_url VARCHAR(256),
    glassdoor_data TEXT,
    crunchbase_data TEXT,
    angellist_data TEXT,
    last_glassdoor_update TIMESTAMP,
    last_crunchbase_upate TIMESTAMP,
    last_angellist_update TIMESTAMP
);

CREATE TABLE people (
    id INT PRIMARY KEY AUTO_INCREMENT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified TIMESTAMP NOT NULL,
    name VARCHAR(64),
    first_name VARCHAR(64),
    last_name VARCHAR(64),
    facebook_id VARCHAR(32),
    linkedin_id VARCHAR(32),
    last_login TIMESTAMP,
    last_facebook_update TIMESTAMP,
    last_linkedin_update TIMESTAMP
);

CREATE TABLE employees (
    person_id INT,
    company_id INT,
    position VARCHAR(32),
    start_date DATE,
    end_date DATE,
    INDEX (person_id),
    INDEX (company_id)
);
