from diagrams import Diagram
from diagrams.aws.storage import S3
from diagrams.aws.integration import SNS
from diagrams.aws.compute import Lambda

with Diagram(filename="s3-event-processing-with-sns-and-lambda", outformat="jpg"):
    S3("S3 Bucket") >> SNS("SNS Topic") >> Lambda("Lambda Function")
