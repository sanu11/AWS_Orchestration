# AWS_Orchestration
Aviate  Cloud Internship (Jan 2016 - March 2016)<br>
The requirement was to start and stop docker containers for a tomcat based webapp at specific times.<br>
AWS services used:<br>
CloudWatch is used to call lambda function at specific times using CRON expressions. <br>
Lambda function is AWS service used to run code for starting and stopping containers.<br>
Docker container management is done using AWS ECS(Elastic Container Service)<br>
The information about EC2 instances to start and services to run is stored in DyamoDB.<br>
The structure of table is given in documentation : <a href="https://github.com/sanu11/AWS_Orchestration/edit/master/ECS.txt">here</a><br>
Python Boto3 library which is AWS API for python is used to write lambda function.






