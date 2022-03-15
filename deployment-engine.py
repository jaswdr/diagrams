from urllib.request import urlretrieve

from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.aws.network import Route53, ELB
from diagrams.aws.compute import Lambda
from diagrams.aws.integration import Eventbridge
from diagrams.aws.integration import SQS
from diagrams.aws.compute import EC2AutoScaling
from diagrams.aws.storage import S3
from diagrams.aws.database import RDSInstance
from diagrams.aws.database import ElasticacheForRedis

graph_attr = {
    "viewport": "1920,1920",
    "fontsize": "45",
    "bgcolor": "transparent",
    "layout":"fdp",
    "splines":"spline",
    "concentrate":"true",
}

github_url = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
github_icon = "/tmp/github.png"
urlretrieve(github_url, github_icon)

with Diagram(filename="deployment-engine", outformat="jpg", graph_attr=graph_attr):
    dns = Route53("DNS")

    with Cluster("External Services"):
        # Github
        github = Custom("Github", github_icon)
        github_oauth = Custom("Github OAuth", github_icon)

    with Cluster("Intake"):
        # Deployment Service Intake
        deploy_svc_intake = Lambda("Deployment Service Intake")
        deploy_svc_intake >> Edge(label="Pull") >> github
        github >> Edge(label="Webhook") >> deploy_svc_intake
        deploy_svc_intake >> github_oauth

        # Webserver
        web_server = Lambda("Web Server")
        web_server >> deploy_svc_intake
        dns >> web_server

    with Cluster("Applications"):
        # Application
        app_lb = ELB("App Load Balancer")
        app_fleet = EC2AutoScaling("App Fleet")
        app_lb >> app_fleet
        dns >> app_lb

    with Cluster("Workers"):
        # Backfill cronjob
        backfill_cronjob = Eventbridge("Backfill CronJob")
        backfill_cronjob >> deploy_svc_intake

        # Workers
        worker_fleet = EC2AutoScaling("Worker Fleet")
        worker_fleet >> app_lb
        worker_fleet >> app_fleet
        worker_queue = SQS("Worker Queue")
        worker_queue >> worker_fleet
        deploy_svc_intake >> worker_queue

        # Object Storage
        obj_storage = S3("Object Storage")
        deploy_svc_intake >> obj_storage
        obj_storage >> worker_fleet

        # Service Discovery
        svc_discovery = Lambda("Service Discovery")
        worker_fleet >> svc_discovery
        app_fleet >> svc_discovery

    with Cluster("Data Layer"):
        # Write API
        write_api_lb = ELB("Write API Load Balancer")
        write_api = Lambda("Write API")
        write_api_lb >> write_api

        db_master_lb = ELB("DB Master Load Balancer")
        write_api >> db_master_lb

        db_master = RDSInstance("DB Master")
        db_master_lb >> db_master
        deploy_svc_intake >> write_api_lb

        # Read API
        read_api_lb = ELB("Read API Load Balancer")
        read_api = Lambda("Read API")
        read_api_lb >> read_api

        db_replica_lb = ELB("DB Read Replica Load Balancer")
        read_api >> db_replica_lb

        db_replica = RDSInstance("DB Read Replica")
        db_replica_lb >> db_replica
        deploy_svc_intake >> read_api_lb

        db_master - db_replica

        # Cache Layer
        db_cache = ElasticacheForRedis("DB Cache")
        read_api >> db_cache

    # Analytics Application
    with Cluster("Analytics"):
        db_replica_analytics = RDSInstance("Analytics DB Read Replica")
        db_replica_analytics - db_master

        analytics_app = Lambda("Analytics Application")
        analytics_app >> db_replica_analytics
        dns >> analytics_app
