from diagrams import Cluster, Diagram, Edge

from diagrams.aws.analytics import KinesisDataStreams, KinesisDataFirehose
from diagrams.aws.compute import Lambda
from diagrams.aws.database import DDB
from diagrams.aws.integration import Eventbridge, SQS
from diagrams.aws.mobile import Amplify
from diagrams.aws.network import APIGateway

from diagrams.onprem.client import User
from diagrams.onprem.compute import Server

graph_attr = {
        "viewport": "1024,768"
}

with Diagram(filename="rent-price-webcrawler", outformat="jpg", direction="TB", show=False):
    cron = Eventbridge("Cron(daily)")

    lambda_crawler = Lambda("Crawler")
    lambda_enrichment = Lambda("Enrichment")
    lambda_search = Lambda("Search")

    sqs_queue = SQS("Offers Enrichment")
    ddb_table = DDB("Offers")

    frontend = Amplify("Frontend")
    api_gateway_entrypoint = APIGateway("API Entrypoint")

    user = User("User")
    webserver = Server("Webserver")

    with Cluster("Collection and Enrichment"):
        cron >> Edge(label="Trigger") >> lambda_crawler << Edge(label="Get Web Page") << webserver
        lambda_crawler >> Edge(label="Send message to Queue") >> sqs_queue
        lambda_crawler >> Edge(label="Write to Table") >> ddb_table
        sqs_queue >> Edge(label="Send message to Listener") >> lambda_enrichment
        lambda_enrichment >> Edge(label="Write to Table") >> ddb_table 

    with Cluster("User interaction"):
        user >> Edge(label="Access") >> frontend
        frontend >> Edge(label="Request") >> api_gateway_entrypoint
        api_gateway_entrypoint >> Edge(label="Trigger") >> lambda_search
        lambda_search >> Edge(label="Query") >> ddb_table
