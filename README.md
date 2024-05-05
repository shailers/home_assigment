Quago home assigment


hello and welcome to my quago home assigment. in the project we aimed to create 
a simulation of a flow of gatharing userdata, aggregating it and then storing it in the db
for reading. hope you like it. 

in order to run it, you can go to "dataset_script" file and run the generate_parquets.py script.
this script will generate 3 batches of datasets of 100000 rows. the datasets will be uploaded to 
the s3 bucket in our aws cloud and from then the flow will start. 

make sure u have set up the correct AWS credentials for the script to be able to access the aws cloud. 
An encrypted credentials file and a secret were sent to you. you can enter the "security" folder and run the "decrypt.py" script to
decrypt the credential files with the secert in order to use them. 


--Notes regarding the flow and implementation -- 

The project architechture is presented in architecture.html . 


1. The flow starts when the script uploads the datasets to the S3 bucket "quago-python-home-task-bucket". The bucket is configured to send an event to our SQS queue "quago-python-home-task-queue" about each dataset created and is tailored to address only the files with the correct prefix and suffix.

2. The SQS queue is configured to achieve scalability, performance, and durability. A dead letter queue was set up in case of failures, so we can check and understand failing messages. It is worth noting that further configuration and fine-tuning can be done to improve; for now, we start with the set configurations and can iterate and fine-tune as needed.

3. The consumer from our SQS queue is the Lambda "dataset_aggregator". The Lambda will consume a message, extract the needed metadata, and read the corresponding Parquet dataset file. The data from the dataset is then aggregated using the pandas library, which makes it ready to be written to the managed Redis by AWS Elasticache. I have chosen the managed service in order to have fewer things to manually manage.

4. In order to write the data to Redis, I use a Lua script for both the atomicity of the writes and to reduce network requests to the database. We are required to maintain exactly-once processing for each file, and for this, we use the file's ETag, which is the hash of the file's contents and thus a unique ID for a unique file. Therefore, the atomicity in the Lua script is also important to enforce this processing policy at the application level. SQS FIFO queue would also provide this but for better throughput, I think it's better to maintain the processing policy at the application level. It is also worth noting that the current Redis cache is set up without demands for encryption at transit for simplicity, but moving forward, it is also important to have this kind of encryption.

5. The Lambda "dataset_aggregator" reads the datasets in batches, which its size can be configured in the ENV variables. I have selected this way of processing in order to not overload the running process memory. The Lambda is using logging to store information, errors, and also logs for debug if needed. The logs are stored in AWS CloudWatch.

6. In order to read the data on the users from the cache, an URL Lambda "read_redis_users_data" was created. This is the URL of the Lambda which is an open endpoint: "https://vk6qiaqcg4tuuf6jd64toqidfe0vhnbe.lambda-url.us-east-1.on.aws/" 

