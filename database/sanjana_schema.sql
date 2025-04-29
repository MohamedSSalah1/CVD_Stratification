-- Create the database
#CREATE DATABASE CVD_RiskDB;
USE CVD_RiskDB;

-- Users Table (For Patients and Clinicians)
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('patient', 'clinician') NOT NULL
);

-- Admins Table (Separate Authentication)
CREATE TABLE Admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('SuperAdmin', 'Manager', 'Support') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patients Table
CREATE TABLE Patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_id INT,
    user_id INT UNIQUE,
    FOREIGN KEY (admin_id) REFERENCES Admins(admin_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Clinicians Table
CREATE TABLE Clinicians (
    clinician_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    specialty VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_id INT,
    user_id INT UNIQUE,
    FOREIGN KEY (admin_id) REFERENCES Admins(admin_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Questionnaire Table
CREATE TABLE Questionnaire (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    question_text TEXT NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    dependencies INT,
    dependencies TEXT,
    question_order INT DEFAULT 0,
    admin_id INT,
    FOREIGN KEY (admin_id) REFERENCES Admins(admin_id) ON DELETE SET NULL
    FOREIGN KEY (dependencies) REFERENCES Questionnaire(question_id) ON DELETE SET NULL
);

-- Responses Table
CREATE TABLE Responses (
    response_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    question_id INT,
    response_type VARCHAR(50), -- e.g., 'categorical', 'boolean', 'numeric'
    numeric_response FLOAT,
    boolean_response BOOLEAN,
    option_selected_id INT,  -- FK to selected option    response_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES Questionnaire(question_id) ON DELETE CASCADE
    FOREIGN KEY (option_selected_id) REFERENCES QuestionResponseOptions(id)

);

-- Questionnaire Response Options Table
CREATE TABLE QuestionResponseOptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT,
    option_text TEXT,
    value_range_start FLOAT,
    value_range_end FLOAT,
    option_label VARCHAR(100),
    FOREIGN KEY (question_id) REFERENCES Questionnaire(question_id)
);

-- Risk Stratification Table
CREATE TABLE Risk_Stratification (
    stratification_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    risk_score DECIMAL(5,2),
    recommendation TEXT,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_id INT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES ML_Models(model_id) ON DELETE SET NULL
);

-- Machine Learning Models Table
CREATE TABLE ML_Models (
    model_id INT AUTO_INCREMENT PRIMARY KEY,
    method VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL
);

-- Patient Outcomes Table
CREATE TABLE Patient_Outcomes (
    outcome_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    outcome_description TEXT NOT NULL,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
);

-- Clinician-Patient Relationship Table
CREATE TABLE Clinician_Patient (
    clinician_id INT,
    patient_id INT,
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (clinician_id, patient_id),
    FOREIGN KEY (clinician_id) REFERENCES Clinicians(clinician_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
);
