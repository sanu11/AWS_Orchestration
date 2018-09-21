# AWS_Orchestration
Aviate  Cloud Internship (Jan 2-16 - March 2016)<br>
The requirement was to start a docker container service for a tomcat at specific times.<br>
CloudWatch is used to call lambda function at specific times using CRON expressions. Lambda function is AWS service used to<br>
run code for starting and stopping containers. Container management is done using AWS ECS(Elastic Container Service)<br>
The information about EC2 instances to start and services to run is stored in DyamoDB.<br>
The structure of table is given in documentation : <a href="https://github.com/sanu11/AWS_Orchestration/blob/master/ECS.docx">here</a><br>






