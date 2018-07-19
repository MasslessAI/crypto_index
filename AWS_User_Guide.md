# AWS User Guide

This document provides a general guide on how to login and use AWS services.

**1. Login massless AWS**

In general, the AWS account with your email address is the root user. AWS recommend NOT to use the root account to perform any daily activities.
Instead, use the root account to create IAM accounts. These IAM accounts can be assigned to various permissions controlled by the root account.

Currently, the following accounts have been created using mark's root account, the default password will be distributed separately.

ang_w
aster_w
lucas_g
mark_z
ming_q

You will need to login via the following URL:

https://massless.signin.aws.amazon.com/console

For first-time login, you will be asked to change your password.

Each of the above accounts has the full admin access to AWS.
This means that it has the full access to use all AWS services, and the full control on existing (EC2/RDS) instances.

**2. Using EC2**

EC2 provides computing capacity on AWS.
All of our processes should and will be run on an EC2 instance.

***2.a  Creating a Key-Pair***

Follow the instructions in the below URL to create a key pair for you own IAM account:
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html

***2.b  Connecting to a Instance***

Use the following information to connect a instance:

Public DNS: ec2-35-182-175-177.ca-central-1.compute.amazonaws.com

Default User: ec2-user

First-time log in, you have to use the private key specified during instance creation.

	Private Key File: provided separately
    
	Then, you will need to add your own public key to the account:
    
		- obtain your public using your private key. This can be done using PuTTYgen. (start with ssh-rsa AAA....)
		
        - echo "ssh-rsa AAAA…" >> /home/ec2_user/.ssh/authorized_keys

Later on, you will be able to use your own private key to log in to the instance. However, you will still need to use the default user (ec2-user) to log in.

***2.c  Using the Instance***

After connecting to the instance, you will be ec2-user.

From here, you can switch to another user. The following users have been created in this instance.

mazhang
cqtrun
lucasgu
angwei
astwang
zuqian

Each of these account has their own home directory. eg /home/mazhang/


***2.c root account***

You can log in as root by running
 
```sudo -s```

Then, you can manage user credentials, install packages and etc.


**3. Using RDS**

RDS provides a relational database service on the cloud.
Currently we use a PostgreSQL instance to store historical prices.
The authentication is done at the database level. 
That is, all users are setup by root account inside a DB instance. Anyone, with a DB-level user/pw can login to the database.
This has nothing to do with the AWS/IAM accounts mentioned above.

***3.a  Connecting to the database instance ***

With whatever the interface of your choice (pgAdmin4, SQLAlchemy, or CLI), you will need the following information:

    - Endpoint: masslessdb.czhchfq2ma03.ca-central-1.rds.amazonaws.com

    - Port: 5432

    - DB Name: masslessDB

    - User-name: XXXX

    - Password: XXXX

Currently, the following users have been setup in the database

angwei
astwang
cqtrun
lucasgu
mazhang
zuqian

All of above accounts have admin access.

The default password will be distributed separately.

To change your password, use the following SQL command:

```ALTER USER user_name WITH PASSWORD 'new_password'```

***3.b  Creating a new database instance ***

You can also create a new database instance for your own need (development, testing, or having fun?)

Use your IAM account, and following the instruction here:

https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Tutorials.WebServerDB.CreateDBInstance.html





