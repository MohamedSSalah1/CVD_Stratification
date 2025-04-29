# Generate the merged and normalized SQL schema for both Sanjana's and Mohammed's tables

#CREATE DATABASE CVD_RiskDB;
USE CVD_RiskDB;
-- ===========================
-- COMMON TABLES
-- ===========================

-- Users Table (shared by all users: patients, clinicians)
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('patient', 'clinician') NOT NULL
);

-- Admins Table
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
CREATE TABLE CVD_risk_Questionnaire (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    question_text TEXT NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    dependencies INT,
    question_order INT DEFAULT 0,
    admin_id INT,
    FOREIGN KEY (admin_id) REFERENCES Admins(admin_id) ON DELETE SET NULL,
    FOREIGN KEY (dependencies) REFERENCES CVD_risk_Questionnaire(question_id) ON DELETE SET NULL
);

-- Questionnaire Response Options Table
CREATE TABLE CVD_risk_QuestionResponseOptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT,
    option_text TEXT,
    value_range_start FLOAT,
    value_range_end FLOAT,
    option_label VARCHAR(100),
    FOREIGN KEY (question_id) REFERENCES CVD_risk_Questionnaire(question_id)
);

-- Responses Table
CREATE TABLE CVD_risk_Responses (
    response_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    question_id INT,
    response_type VARCHAR(50),
    numeric_response FLOAT,
    boolean_response BOOLEAN,
    option_selected_id INT,
    response_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES CVD_risk_Questionnaire(question_id) ON DELETE CASCADE,
    FOREIGN KEY (option_selected_id) REFERENCES CVD_risk_QuestionResponseOptions(id)
);

-- Clinician-Patient Mapping
CREATE TABLE CVD_risk_Clinician_Patient (
    clinician_id INT,
    patient_id INT,
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (clinician_id, patient_id),
    FOREIGN KEY (clinician_id) REFERENCES Clinicians(clinician_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
);

-- Features Table
CREATE TABLE batch_CVD_Risk_Features (
    feature_id INT AUTO_INCREMENT PRIMARY KEY,
    feature_name VARCHAR(255) NOT NULL,
    feature_description TEXT
);

-- Model-Feature Table
CREATE TABLE batch_CVD_Risk_Model_Features (
    model_id INT NOT NULL,
    feature_id INT NOT NULL,
    PRIMARY KEY (model_id, feature_id),
    FOREIGN KEY (model_id) REFERENCES ML_Models(model_id),
    FOREIGN KEY (feature_id) REFERENCES batch_CVD_Risk_Features(feature_id)
);

-- Patient Outcomes Table
CREATE TABLE CVD_risk_Patient_Outcomes (
    outcome_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    outcome_description TEXT NOT NULL,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES CVD_risk_Patients(patient_id) ON DELETE CASCADE
);

-- Model Table
CREATE TABLE ML_Models (
    `model_id` INT(11) NOT NULL AUTO_INCREMENT,
    `model_name` VARCHAR(255) NOT NULL,  -- E.g. 'Classical COX-PH Model', 'Elastic Net COX-PH' 
    `model_type` VARCHAR(100) NOT NULL,  -- E.g. 'CNN', 'XGBoost', 'Logistic Regression'

    PRIMARY KEY (`model_id`)
);
-- ===========================
-- SANJANA'S SCHEMA (CVD_risk_)
-- ===========================

-- Risk Stratification Scores Table
CREATE TABLE batch_CVD_Risk_Stratification (
    risk_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    model_id INT NOT NULL,
    risk_score DECIMAL(5,2) NOT NULL,
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (model_id) REFERENCES ML_Models(model_id)
);

-- ===========================
-- MOHAMMED'S SCHEMA (batch_CVD_Risk_)
-- ===========================

-- Output Visuals Table
CREATE TABLE batch_CVD_Risk_Output (
    output_id INT AUTO_INCREMENT PRIMARY KEY,
    risk_id INT NOT NULL,
    plot_type VARCHAR(100) NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (risk_id) REFERENCES batch_CVD_Risk_Risk(risk_id)
);

-- Risk Stratification (live system use)
CREATE TABLE CVD_risk_Risk_Stratification (
    stratification_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    risk_score DECIMAL(5,2),
    recommendation TEXT,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_id INT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES ML_Models(model_id) ON DELETE SET NULL
);


