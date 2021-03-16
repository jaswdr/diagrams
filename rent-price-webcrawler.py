from diagrams import Cluster, Diagram, Edge

from diagrams.aws.analytics import KinesisDataStreams, KinesisDataFirehose
from diagrams.aws.compute import Lambda
from diagrams.aws.database import DDB
from diagrams.aws.integration import Eventbridge, SQS
from diagrams.aws.mobile import Amplify
from diagrams.aws.network import APIGateway, Route53
from diagrams.aws.storage import S3

from diagrams.onprem.client import User
from diagrams.onprem.compute import Server

graph_attr = {
        "viewport": "1024,768"
}

with Diagram(filename="rent-price-webcrawler", outformat="jpg", direction="LR", show=False):
    cron = Eventbridge("Cron(daily)")
    bucket_raw = SQS("Raw Data")
    bucket_static = S3("Static Data")

    lambda_crawler = Lambda("Crawler")
    lambda_extractor = Lambda("Extractor")
    lambda_aggregator = Lambda("Aggregator")
    lambda_search = Lambda("Search")

    ddb_table = DDB("Offers")

    frontend = Amplify("Frontend")
    api_dns_entrypoint = Route53("API Entrypoint")
    api_gateway_entrypoint = APIGateway("API Entrypoint")

    user = User("User")
    webserver = Server("Webserver")

    with Cluster("Collection and Enrichment"):
        cron >> Edge(label="Fires") >> lambda_crawler << Edge(label="Get Web Page") << webserver
        lambda_crawler >> Edge(label="Saves Raw Data") >> bucket_raw
        bucket_raw >> Edge(label="Send to Listeners") >> lambda_extractor >> Edge(label="Save Enrichment Data") >> ddb_table
        ddb_table >> Edge(label="Publish to Stream") >> lambda_aggregator
        lambda_aggregator >> Edge(label="Save Aggregated Data") >> bucket_static

    with Cluster("User interaction"):
        user >> Edge(label="Access") >> frontend
        frontend >> Edge(label="Request") >> api_dns_entrypoint >> Edge(label="Resolves") >> api_gateway_entrypoint
        api_gateway_entrypoint >> Edge(label="Trigger") >> lambda_search >> Edge(label="Query") >> ddb_table
        lambda_search >> Edge(label="Get Static") >> bucket_static
