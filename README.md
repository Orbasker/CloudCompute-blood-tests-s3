# CloudCompute-blood-tests-s3
Cloud computing course, blood test assignments to validate and upload to S3 buckets

# Blood Test Storage System

This repository contains the implementation of a secure system for storing and transferring blood test data from hospitals to secure cloud storage.

![System Architecture](images/system_architecture.png)

## Table of Contents
- [Introduction](#introduction)
- [Architecture](#architecture)
- [Attack Vector and Attack Surface](#attack-vector-and-attack-surface)
- [Implementation](#implementation)
  - [Set Up S3 Buckets](#set-up-s3-buckets)
  - [Define Data Structure](#define-data-structure)
  - [Validation Script](#validation-script)
  - [Cron Job](#cron-job)
  - [Demo Video](#demo-video)
- [Data Transfer Method](#data-transfer-method)
- [Invalid Files Notifications](#invalid-files-notifications)
- [Technology Stack](#technology-stack)

## Introduction
This system ensures the secure storage and transfer of blood test data using client-side encryption, secure file transfer protocols, and data validation processes.

![Data Flow](images/data_flow.png)

## Architecture
The architecture involves a Linux server, Amazon S3 buckets, and client-side software for secure and validated data transfers.

## Attack Vector and Attack Surface
- **Attack Vector:** Our Linux server.
- **Attack Surface:** The file on the Linux server where data is initially stored.

## Implementation

### Set Up S3 Buckets
Create two S3 buckets:
- One for valid data
- One for invalid data

![S3 Buckets](images/s3_buckets.png)

### Define Data Structure
Define the structure of a valid blood sample:

**Valid:**
- `patient_id`: int
- `sample_id`: int
- `result`: string
- Extra keys are accepted

**Invalid Examples:**
- Empty key
- Missing key
- Incorrect type

### Validation Script
Develop and implement a script named `validator` to:
- Check for new files in the `blood_test` folder.
- Move files to a temporary folder and run the validation script.
- Upload files to the correct S3 bucket based on validation results.
- Optionally, alert the security admin for invalid blood tests.

### Cron Job
Implement the validation script as a cron job to run at regular intervals.

### Demo Video
Include a demo video showcasing the script functionality.

### Script Functionality
- Check for files in the `blood_test` folder.
- Move completed files to a temporary folder.
- Validate each file.
- Transfer files to the appropriate S3 bucket (valid or invalid) based on validation results.
- Notify if a file is damaged or corrupted.

## Data Transfer Method
Use FileZilla for a graphical user interface to transfer files using SFTP.

## Invalid Files Notifications
- **Notification Mechanism:** Notify the security admin by email when an invalid file is detected.
- **Email Content:** Include the path to the file and the reason it is failing.

## Technology Stack
- **Linux Server:** Hosting the validation script and serving as the initial storage point.
- **Amazon S3:** Secure cloud storage for segregating valid and invalid data.
- **FileZilla:** Client software for graphical file transfer interface using SFTP.
- **Gmail API:** For sending notifications regarding invalid files.
