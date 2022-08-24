DROP TABLE IF EXISTS todos;
DROP TABLE IF EXISTS conversation_history;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users_lessons;
DROP TABLE IF EXISTS users_courses;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS jobs_skills;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS categories;


CREATE TABLE categories
(
	id         INT          NOT NULL AUTO_INCREMENT,
	name       VARCHAR(255) NOT NULL,
	created_at DATETIME     NOT NULL,
	updated_at DATETIME     NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE companies
(
	id         INT         NOT NULL AUTO_INCREMENT,
	name       VARCHAR(50) NOT NULL,
	address    TEXT        NOT NULL,
	created_at DATETIME    NOT NULL,
	updated_at DATETIME    NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE jobs
(
	id         INT         NOT NULL AUTO_INCREMENT,
	company_id INT         NULL,
	title      VARCHAR(50) NOT NULL,
	level      INT         NOT NULL,
	created_at DATETIME    NOT NULL,
	updated_at DATETIME    NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (company_id) REFERENCES companies (id)
);

CREATE TABLE teams
(
	id         INT         NOT NULL AUTO_INCREMENT,
	company_id INT         NOT NULL,
	name       VARCHAR(25) NOT NULL,
	mascot     TEXT        NULL,
	created_at DATETIME    NOT NULL,
	updated_at DATETIME    NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (company_id) REFERENCES companies (id)
);

CREATE TABLE users
(
	id              INT          NOT NULL AUTO_INCREMENT,
	company_id      INT          NOT NULL,
	job_id          INT          NULL,
	team_id         INT          NULL,
	first_name      VARCHAR(255) NOT NULL,
	last_name       VARCHAR(255) NULL,
	email           VARCHAR(255) NOT NULL,
	password        VARCHAR(30)  NOT NULL,
	street_address1 VARCHAR(255) NULL,
	street_address2 VARCHAR(255) NULL,
	city            VARCHAR(255) NULL,
	state           VARCHAR(50)  NULL,
	zip             VARCHAR(15)  NULL,
	timezone        VARCHAR(50)  NOT NULL,
	status          enum ('new', 'action_taken', 'deactivated') DEFAULT 'new',
	created_at      DATETIME     NOT NULL,
	updated_at      DATETIME     NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (company_id) REFERENCES companies (id),
	FOREIGN KEY (job_id) REFERENCES jobs (id)
);

CREATE TABLE goals
(
	id          INT         NOT NULL AUTO_INCREMENT,
	user_id     INT         NOT NULL,
	parent_id   INT         NULL,
	category_id INT         NULL,
	name        TEXT        NOT NULL,
	priority    INT         NOT NULL DEFAULT 99,
	start_date  DATETIME    NULL,
	due_date    DATETIME    NULL,
	duration    VARCHAR(10) NULL,
	details     TEXT        NULL,
	why         TEXT        NULL,
	result      TEXT        NULL,
	done        INT         NOT NULL DEFAULT 0,
	created_at  DATETIME    NOT NULL,
	updated_at  DATETIME    NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES users (id),
	FOREIGN KEY (parent_id) REFERENCES goals (id) ON DELETE CASCADE,
	FOREIGN KEY (category_id) REFERENCES categories (id)
);

CREATE TABLE skills
(
	id          INT      NOT NULL AUTO_INCREMENT,
	name        TEXT     NOT NULL,
	skill_level INT      NOT NULL,
	created_at  DATETIME NOT NULL,
	updated_at  DATETIME NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE courses
(
	id          INT      NOT NULL AUTO_INCREMENT,
	skill_id    INT      NULL,
	name        TEXT     NOT NULL,
	link        TEXT     NULL,
	description TEXT     NULL,
	total_time  INT      NOT NULL, /* minutes */
	created_at  DATETIME NOT NULL,
	updated_at  DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (skill_id) REFERENCES skills (id)
);

CREATE TABLE lessons
(
	id          INT      NOT NULL AUTO_INCREMENT,
	course_id   INT      NOT NULL,
	seq_num     INT      NOT NULL,
	name        TEXT     NOT NULL,
	link        TEXT     NULL,
	description TEXT     NULL,
	duration    INT      NOT NULL, /* minutes */
	created_at  DATETIME NOT NULL,
	updated_at  DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (course_id) REFERENCES courses (id)
);

CREATE TABLE jobs_skills
(
	job_id   INT REFERENCES jobs (id),
	skill_id INT REFERENCES skills (id)
);

CREATE TABLE users_courses
(
	user_id     INT REFERENCES users (id),
	course_id   INT REFERENCES courses (id),
	status      ENUM ('Requested', 'Scheduled', 'Started', 'Completed') DEFAULT 'Requested',
	certificate VARCHAR(255) NULL,
	created_at  DATETIME     NOT NULL,
	updated_at  DATETIME     NOT NULL
);

CREATE TABLE users_lessons
(
	user_id         INT REFERENCES users (id),
	course_id       INT REFERENCES courses (id),
	lesson_id       INT REFERENCES lessons (id),
	status          ENUM ('Requested', 'Scheduled', 'Started', 'Completed') DEFAULT 'Requested',
	scheduled_start DATETIME NOT NULL,
	scheduled_end   DATETIME NOT NULL,
	final_comments  TEXT     NULL,
	created_at      DATETIME NOT NULL,
	updated_at      DATETIME NOT NULL
);

CREATE TABLE events
(
	id          INT          NOT NULL AUTO_INCREMENT,
	user_id     INT          NOT NULL,
	goal_id     INT          NULL,
	title       VARCHAR(255) NOT NULL,
	description TEXT         NULL,
	start_time  DATETIME     NOT NULL,
	end_time    DATETIME     NOT NULL,
	color       VARCHAR(255) DEFAULT '#6daa6d',
	created_at  DATETIME     NOT NULL,
	updated_at  DATETIME     NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES users (id),
	FOREIGN KEY (goal_id) REFERENCES goals (id) ON DELETE CASCADE
);

CREATE TABLE conversation_history
(
	id          INT          NOT NULL AUTO_INCREMENT,
	user_id     INT          NULL,
	session_id  VARCHAR(50)  NULL,
	type        VARCHAR(20)  NOT NULL, -- "inquiry", "login", "logout", "change_screen", "register", "edit profile".
	question    VARCHAR(511) NULL,
	response    VARCHAR(255) NULL,
	ip_address  VARCHAR(30)  NULL,
	device_type VARCHAR(255) NULL,
	timestamp   DATETIME     NOT NULL DEFAULT CURRENT_TIME(),
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS `todos`
(
	`id`           INT          NOT NULL AUTO_INCREMENT,
	`user_id`      INT          NOT NULL,
	`parent_id`    INT          NULL,
	`parent_table` VARCHAR(50)  NULL,
	`category_id`  INT          NULL,
	`name`         VARCHAR(255) NOT NULL,
	`priority`     INT UNSIGNED NOT NULL,
	`start_date`   DATETIME     NULL,
	`due_date`     DATETIME     NULL,
	`duration`     VARCHAR(10)  NULL,
	`details`      TEXT         NULL,
	`why`          VARCHAR(255) NULL,
	`result`       TEXT         NULL,
	`done`         TINYINT(1)   NOT NULL DEFAULT 0,
	`created`      TIMESTAMP    NULL,
	`updated`      TIMESTAMP    NULL,
	PRIMARY KEY (`id`),
	FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
	FOREIGN KEY (parent_id) REFERENCES todos (id) ON DELETE CASCADE,
	FOREIGN KEY (category_id) REFERENCES categories (id)
);

INSERT INTO categories (id, name, created_at, updated_at)
values (1, "Education", "2020-01-02", "2020-01-05");
INSERT INTO categories (id, name, created_at, updated_at)
values (2, "Creative", "2020-01-02", "2020-01-05");
INSERT INTO categories (id, name, created_at, updated_at)
values (3, "Health", "2020-01-02", "2020-01-05");
INSERT INTO categories (id, name, created_at, updated_at)
values (4, "Sports", "2020-01-02", "2020-01-05");
INSERT INTO categories (id, name, created_at, updated_at)
values (5, "Other", "2020-01-02", "2020-01-05");

INSERT INTO companies
values (1, "Data Networks Corporation", "Mountain View, CA", "2020-01-02", "2020-08-05 16:33");
INSERT INTO companies
values (2, "Alpha-tech Company", "Sunnyvale, CA", "2020-09-22", "2021-04-11 09:18");

INSERT INTO jobs
values (1, 1, "Data Scientist 1", 1, "2020-01-02", "2020-08-05 11:33");
INSERT INTO jobs
values (2, 1, "Data Scientist 2", 2, "2020-01-06", "2020-08-04 18:43");
INSERT INTO jobs
values (3, 1, "Senior Data Scientist", 3, "2020-01-03", "2020-07-09 16:26");
INSERT INTO jobs
values (4, 1, "Lead Data Scientist", 4, "2020-01-03", "2020-07-09 16:26");
INSERT INTO jobs
values (5, 1, "Software Engineer", 1, "2020-04-04", "2020-11-22 12:09");
INSERT INTO jobs
values (6, 2, "Software Engineer", 1, "2020-01-02", "2021-01-05 18:29");
INSERT INTO jobs
values (7, 2, "Sr. Software Engineer", 2, "2020-05-02", "2020-09-27 09:49");

INSERT INTO teams
values (1, 1, "Giants", "giant", "2020-01-02", "2020-07-05 20:17");
INSERT INTO teams
values (2, 1, "Bobcats", "big cat", "2020-06-08", "2020-01-05 09:39");
INSERT INTO teams
values (3, 1, "Wildcats", "wildcat", "2021-01-20", "2021-02-05 05:34");
INSERT INTO teams
values (4, 1, "Chargers", "palladin", "2021-01-20", "2021-02-05 05:34");

INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, street_address1,
				   street_address2, city, state, zip, timezone, created_at, updated_at)
values (1, 1, 1, 1, "John", "Smith", "john.smith@gmail.com", "123456",
		"123 Main Street", "Apt 100", "Palo Alto", "CA", "94303",
		"US/Pacific", "2020-01-02", "2020-07-05 20:17");

INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, street_address1,
				   street_address2, city, state, zip, timezone, created_at, updated_at)
values (2, 1, 1, 1, "Hank", "Jackson", "hank.jackson@gmail.com", "123456",
		"500 University Avenue", null, "Palo Alto", "CA", "94303",
		"US/Pacific", "2020-06-08", "2020-01-05 09:39");

INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, street_address1,
				   street_address2, city, state, zip, timezone, created_at, updated_at)
values (3, 1, 6, 1, "Kwabena", "Donkor", "kwabena.donkor@gmail.com", "123456",
		"400 Castro Street", null, "Mountain View", "CA", "94040",
		"US/Pacific", "2021-01-20", "2021-02-05 05:34");

INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, street_address1,
				   street_address2, city, state, zip, timezone, created_at, updated_at)
values (4, 1, 6, 1, "Dave", "Gilson", "david.gilson@gmail.com", "123456",
		"800 Blossom Hill Road", "Unit P-383", "Los Gatos", "CA", "95124",
		"US/Pacific", "2021-01-20", "2021-02-05 05:34");

INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (5, 1, 6, 2, "Chenzi", "Xu", "chenzi.xu@gmail.com", "123456", "US/Pacific", "2021-01-20", "2021-02-05 05:34");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (6, 1, 6, 2, "David", "Larckar", "david.larckar@gmail.com", "123456", "US/Pacific", "2021-01-20",
		"2021-02-05 05:34");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (7, 1, 6, 2, "Peter", "Baird", "peter.baird@gmail.com", "123456", "US/Pacific", "2021-01-20",
		"2021-02-05 05:34");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (8, 1, 6, 2, "Amit", "Seru", "amit.seru@gmail.com", "123456", "US/Pacific", "2021-01-20", "2021-02-05 05:34");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (9, 1, 6, 2, "Amanda", "So", "amanda.so@gmail.com", "123456", "US/Pacific", "2021-01-20", "2021-02-05 05:34");

INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (10, 1, 1, 3, "Viet", "Nguyen", "viet.nguyen@gmail.com", "123456", "US/Pacific", "2020-01-02",
		"2020-07-05 20:17");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (11, 1, 1, 3, "Monica", "Juzwiak", "monica.juzwiak@gmail.com", "123456", "US/Pacific", "2020-06-08",
		"2020-01-05 09:39");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (12, 1, 6, 3, "Xieia", "Wu", "Xieia.wu@gmail.com", "123456", "US/Pacific", "2021-01-20", "2021-02-05 05:34");

INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (13, 1, 6, 4, "Jaime", "Munoz", "jaime.munoz@gmail.com", "123456", "US/Pacific", "2021-01-20",
		"2021-02-05 05:34");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (14, 1, 6, 4, "Sally", "Riorden", "sally.riorden@gmail.com", "123456", "US/Pacific", "2021-01-20",
		"2021-02-05 05:34");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (15, 1, 6, 4, "Julia", "Kane", "julia.kane@gmail.com", "123456", "US/Pacific", "2021-01-20", "2021-02-05 05:34");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (16, 1, 6, 4, "Tan", "Nguyen", "tan.nguyen@gmail.com", "123456", "US/Pacific", "2021-01-20", "2021-02-05 05:34");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (17, 1, 6, 4, "Szu-chi", "Huang", "szuchi.huang@gmail.com", "123456", "US/Pacific", "2021-01-20",
		"2021-02-05 05:34");

INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (101, 2, 6, 4, "Jim", "Friedlich", "jim.friedlich@gmail.com", "123456", "US/Pacific", "2021-01-20",
		"2021-02-05 05:34");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (102, 2, 6, 4, "Glenn", "Solomon", "glenn.solomon@gmail.com", "123456", "US/Pacific", "2021-01-20",
		"2021-02-05 05:34");
INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (103, 2, 6, 4, "Andrea", "Rice", "andrea.rice@gmail.com", "123456", "US/Pacific", "2021-01-20",
		"2021-02-05 05:34");

INSERT INTO users (id, company_id, job_id, team_id, first_name, last_name, email, password, timezone, created_at,
				   updated_at)
values (110, 1, 1, 1, "Junling", "Hu", "junlinghu@gmail.com", "123456", "US/Pacific",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

ALTER TABLE users
	ADD COLUMN IF NOT EXISTS google_access_token VARCHAR(255) null;
ALTER TABLE users
	ADD COLUMN IF NOT EXISTS google_refresh_token VARCHAR(255) null;
ALTER TABLE users
	CHANGE COLUMN `password` `password` VARCHAR(100) NULL;

ALTER TABLE users
	ADD COLUMN IF NOT EXISTS profile_image VARCHAR(255) null;
ALTER TABLE users
	ADD COLUMN IF NOT EXISTS background INT null;

ALTER TABLE `events`
	ADD COLUMN IF NOT EXISTS `source` VARCHAR(50) null;
ALTER TABLE `events`
	ADD COLUMN IF NOT EXISTS `event_external_id` VARCHAR(80) null;
ALTER TABLE `events`
	CHANGE COLUMN `title` `title` TEXT NULL;
ALTER TABLE `events`
	CHANGE COLUMN `event_external_id` `event_external_id` VARCHAR(1025) NULL;

INSERT INTO skills
values (1, "Databases", 1, "2021-01-22", "2021-02-11 02:56");
INSERT INTO skills
values (2, "NLP", 1, "2021-01-22", "2021-02-11 02:56");
INSERT INTO skills
values (3, "Machine Learning", 1, "2021-01-23", "2021-02-11 03:06");
INSERT INTO skills
values (4, "Machine Learning", 2, "2021-01-24", "2021-02-12 18:56");
INSERT INTO skills
values (5, "Time Management", 1, "2021-01-24", "2021-02-12 19:36");
INSERT INTO skills
values (6, "Public Speaking", 1, "2021-01-24", "2021-02-11 20:56");

INSERT INTO jobs_skills
values (2, 1);
INSERT INTO jobs_skills
values (2, 2);
INSERT INTO jobs_skills
values (2, 4);
INSERT INTO jobs_skills
values (2, 5);
INSERT INTO jobs_skills
values (2, 6);

INSERT INTO courses
values (1, 1, "Advanced Databases", "https://databaselearning.com", "Advanced Databases class", 60, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO courses
values (2, 2, "Natural Language Processing", "https://nlptutor.com", "Introduction to NLP", 60, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO courses
values (3, 4, "Machine Learning", "https://ml.com", "Advanced machine learning", 60, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO courses
values (4, 5, "Time Management", "https://timemanagement.com", "How to manage time efficiently", 90,
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO courses
values (5, 6, "Public Speaking", "https://toastmasters.org", "Toastmaster training", 60, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());

INSERT INTO lessons
values (1, 1, 1, "Lesson 1", "https://databaselearning.com", "Introduction", 60, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (2, 1, 2, "Lesson 2", "https://databaselearning.com", "How to design DB", 45, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (3, 2, 1, "Lesson 1", "https://nlptutor.com", "Introduction", 30, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (4, 2, 2, "Lesson 2", "https://nlptutor.com", "Concepts", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (5, 2, 3, "Lesson 3", "https://nlptutor.com", "Words as Tokens", 40, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (6, 2, 4, "Lesson 4", "https://nlptutor.com", "Tokenizing", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (7, 2, 5, "Lesson 5", "https://nlptutor.com", "Tokenizing", 40, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (8, 2, 6, "Lesson 6", "https://nlptutor.com", "Parsing 1", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (9, 2, 7, "Lesson 7", "https://nlptutor.com", "Parsing 2", 70, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (10, 2, 8, "Lesson 8", "https://nlptutor.com", "Text Matching 1", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (11, 2, 9, "Lesson 9", "https://nlptutor.com", "Text Matching 2", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (12, 2, 10, "Lesson 10", "https://nlptutor.com", "Neural Networks", 30, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (13, 2, 11, "Lesson 11", "https://nlptutor.com", "Recurrent NNs", 30, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (14, 2, 12, "Lesson 12", "https://nlptutor.com", "Transformers", 30, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (15, 3, 1, "Lesson 1", "https://ml.com", "Introduction", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (16, 3, 2, "Lesson 2", "https://ml.com", "Logic", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (17, 3, 3, "Lesson 3", "https://ml.com", "Knowledge", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (18, 3, 4, "Lesson 4", "https://ml.com", "Reasoning", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (19, 3, 5, "Lesson 5", "https://ml.com", "Probability", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (20, 3, 6, "Lesson 6", "https://ml.com", "Natural Language", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (21, 3, 7, "Lesson 7", "https://ml.com", "Vision", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (22, 3, 8, "Lesson 8", "https://ml.com", "Conclusion", 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO lessons
values (23, 4, 1, "Lesson 1", "https://timemanagement.com", "Introduction", 30, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (24, 4, 2, "Lesson 2", "https://timemanagement.com", "Scheduling", 30, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (25, 4, 3, "Lesson 3", "https://timemanagement.com", "Organizing", 30, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (26, 5, 1, "Lesson 1", "https://toastmasters.org", "Introduction", 30, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (27, 5, 2, "Lesson 2", "https://toastmasters.org", "Organizing your Speech", 30, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (28, 5, 3, "Lesson 3", "https://toastmasters.org", "Your Body Speaks", 60, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO lessons
values (29, 5, 4, "Lesson 4", "https://toastmasters.org", "The Influential Speech", 30, CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());

INSERT INTO users_courses
values (1, 1, "Scheduled", NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO users_courses
values (1, 2, "Scheduled", NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO users_lessons
values (1, 1, 1, "Scheduled", ADDTIME(CURRENT_DATE(), "0 17:00:00"), ADDTIME(CURRENT_DATE(), "0 18:00:00"), NULL,
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO users_lessons
values (1, 1, 2, "Scheduled", ADDTIME(CURRENT_DATE(), "1 17:00:00"), ADDTIME(CURRENT_DATE(), "1 18:00:00"), NULL,
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO users_lessons
values (1, 2, 3, "Scheduled", ADDTIME(CURRENT_DATE(), "2 17:00:00"), ADDTIME(CURRENT_DATE(), "2 18:00:00"), NULL,
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO users_lessons
values (1, 2, 4, "Scheduled", ADDTIME(CURRENT_DATE(), "3 17:00:00"), ADDTIME(CURRENT_DATE(), "3 18:00:00"), NULL,
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO users_courses
values (2, 2, "Scheduled", NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO users_courses
values (2, 3, "Scheduled", NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO users_courses
values (3, 2, "Scheduled", NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO users_courses
values (3, 3, "Scheduled", NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO users_courses
values (3, 4, "Scheduled", NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO goals (id, user_id, start_date, name, priority, why, created_at, updated_at)
values (1, 1, "2022-06-01", 'Prepare for concert in August', 1, "parents will be attending", "2022-05-20",
		"2022-05-21");
INSERT INTO goals (id, user_id, start_date, name, priority, why, created_at, updated_at)
values (2, 1, "2022-06-01", 'Study for SATs', 2, "needed for college application", "2022-05-20", "2022-05-21");

INSERT INTO goals (id, user_id, start_date, name, priority, created_at, updated_at)
values (3, 2, "2022-06-01", 'Softball tournament', 1, "2022-05-20", "2022-05-21");
INSERT INTO goals (id, user_id, start_date, name, priority, why, created_at, updated_at)
values (4, 2, "2022-06-01", 'Study for SATs', 2, "needed for college application", "2022-05-20", "2022-05-21");

INSERT INTO goals (id, user_id, start_date, name, priority, created_at, updated_at)
values (5, 3, "2022-06-01", 'Perform in Hamlet production in August', 1, "2022-05-20", "2022-05-21");
INSERT INTO goals (id, user_id, start_date, name, priority, created_at, updated_at)
values (6, 3, "2022-06-01", 'Walk every day', 2, "2022-05-20", "2022-05-21");

INSERT INTO goals (id, user_id, start_date, name, priority, created_at, updated_at)
values (7, 4, "2022-06-01", 'Enter painting in art show for August', 1, "2022-05-20", "2022-05-21");
INSERT INTO goals (id, user_id, start_date, name, priority, why, created_at, updated_at)
values (8, 4, "2022-06-01", 'Prepare college app materials', 2, "Go to college", "2022-05-20", "2022-05-21");

INSERT INTO goals (id, user_id, start_date, name, priority, why, created_at, updated_at)
values (9, 1, "2022-07-01", 'Prepare for concert in August', 1, "parents will be attending", "2022-05-20",
		"2022-05-21");
INSERT INTO goals (id, user_id, start_date, name, priority, why, created_at, updated_at)
values (10, 1, "2022-07-01", 'Study for SATs', 2, "needed for college application", "2022-05-20", "2022-05-21");

INSERT INTO goals (id, user_id, start_date, name, priority, created_at, updated_at)
values (11, 2, "2022-07-01", 'Softball tournament', 1, "2022-05-20", "2022-05-21");
INSERT INTO goals (id, user_id, start_date, name, priority, why, created_at, updated_at)
values (12, 2, "2022-07-01", 'Study for SATs', 2, "needed for college application", "2022-05-20", "2022-05-21");

INSERT INTO goals (id, user_id, start_date, name, priority, created_at, updated_at)
values (13, 3, "2022-07-01", 'Perform in Hamlet production in August', 1, "2022-05-20", "2022-05-21");
INSERT INTO goals (id, user_id, start_date, name, priority, created_at, updated_at)
values (14, 3, "2022-07-01", 'Walk every day', 2, "2022-05-20", "2022-05-21");

INSERT INTO goals (id, user_id, start_date, name, priority, created_at, updated_at)
values (15, 4, "2022-07-01", 'Enter painting in art show for August', 1, "2022-05-20", "2022-05-21");
INSERT INTO goals (id, user_id, start_date, name, priority, why, created_at, updated_at)
values (16, 4, "2022-07-01", 'Prepare college app materials', 2, "Go to college", "2022-05-20", "2022-05-21");


INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (21, 1, 1, "2022-06-20", "Music practice session", 3, ADDTIME(CURRENT_DATE(), "7 0:00:00"), "8 hours", null,
		"Violin concerto",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (22, 1, 2, "2022-06-20", "Read SAT book, chapter 1", 1, ADDTIME(CURRENT_DATE(), "5 0:00:00"),
		"4 hours", "Book was given to me by advisor",
		"Keep up to date", CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (23, 2, 3, "2022-06-20", "softball practice", 2, ADDTIME(CURRENT_DATE(), "4 0:00:00"), "12 hours", null, "",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (24, 2, 4, "2022-06-20", "Read SAT book, chapter 1", 2, ADDTIME(CURRENT_DATE(), "4 0:00:00"), "12 hours", null,
		"",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (25, 3, 5, "2022-06-20", "Buy the book for Hamlet", 2, ADDTIME(CURRENT_DATE(), "4 0:00:00"), "5 hours", null, "",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (26, 3, 6, "2022-06-20", "Walking time", 2, ADDTIME(CURRENT_DATE(), "4 0:00:00"), "5 hours", null, "",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (27, 4, 7, "2022-06-20", "buy art supplies", 2, ADDTIME(CURRENT_DATE(), "4 0:00:00"), "5 hours", null, "",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (28, 4, 8, "2022-06-20", "Read SAT book, chapter 2", 2, ADDTIME(CURRENT_DATE(), "4 0:00:00"), "5 hours", null,
		"",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (29, 1, 1, "2022-06-27", "Music practice session", 3, ADDTIME(CURRENT_DATE(), "7 0:00:00"), "8 hours", null,
		"Violin concerto",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (30, 1, 2, "2022-06-27", "Read SAT book, chapter 1", 1, ADDTIME(CURRENT_DATE(), "5 0:00:00"),
		"4 hours", "Book was given to me by advisor",
		"Keep up to date", CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (31, 2, 3, "2022-06-27", "softball practice", 2, ADDTIME(CURRENT_DATE(), "4 0:00:00"), "12 hours", null, "",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (32, 2, 4, "2022-06-27", "Read SAT book, chapter 1", 2, ADDTIME(CURRENT_DATE(), "4 0:00:00"), "12 hours", null,
		"",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (33, 1, 9, "2022-07-04", "Music practice session", 3, ADDTIME(CURRENT_DATE(), "7 0:00:00"), "8 hours", null,
		"Violin concerto",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (34, 1, 10, "2022-07-04", "Read SAT book, chapter 1", 1, ADDTIME(CURRENT_DATE(), "5 0:00:00"),
		"4 hours", "Book was given to me by advisor",
		"Keep up to date", CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (35, 1, 9, "2022-07-11", "Music practice session", 3, ADDTIME(CURRENT_DATE(), "7 0:00:00"), "8 hours", null,
		"Violin concerto",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, due_date, duration, details, why,
				   created_at, updated_at)
values (36, 1, 10, "2022-07-11", "Read SAT book, chapter 1", 1, ADDTIME(CURRENT_DATE(), "5 0:00:00"),
		"4 hours", "Book was given to me by advisor",
		"Keep up to date", CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, duration, details, why, created_at,
				   updated_at)
values (51, 1, 1, "2022-06-26", "Music practice", 1, 6, "Music practice", "Music practice",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, duration, details, why, created_at,
				   updated_at)
values (52, 1, 2, "2022-06-26", "study time", 2, 3, null, "study time", CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());

INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, duration, details, why, done, created_at,
				   updated_at)
values (53, 2, 3, "2022-06-26", "softball time", 1, 5, null, "", 0,
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, duration, details, why, done, created_at,
				   updated_at)
values (54, 3, 4, "2022-06-26", "Study the material", 1, 5, null, "", 0,
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, duration, details, why, created_at,
				   updated_at)
values (55, 4, 9, "2022-07-04", "Music practice", 1, 6, "Music practice", "Music practice",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, duration, details, why, created_at,
				   updated_at)
values (56, 5, 10, "2022-07-04", "study time", 2, 3, null, "study time", CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, duration, details, why, created_at,
				   updated_at)
values (57, 6, 9, "2022-07-12", "Music practice", 1, 6, "Music practice", "Music practice",
		CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO goals (id, user_id, parent_id, start_date, name, priority, duration, details, why, created_at,
				   updated_at)
values (58, 7, 10, "2022-07-12", "study time", 2, 3, null, "study time", CURRENT_TIMESTAMP(),
		CURRENT_TIMESTAMP());
