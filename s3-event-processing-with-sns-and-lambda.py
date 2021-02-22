from diagrams import Diagram
from diagrams.aws.storage import S3
from diagrams.aws.integration import SNS
from diagrams.aws.compute import Lambda

graph_attr = {
        "viewport": "450,350"
}

with Diagram(filename="s3-event-processing-with-sns-and-lambda", outformat="jpg", graph_attr=graph_attr):
    S3("S3 Bucket") >> SNS("SNS Topic") >> [Lambda("Lambda Function 1"), Lambda('Lambda Function 2')]
