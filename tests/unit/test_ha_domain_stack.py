import aws_cdk as core
import aws_cdk.assertions as assertions
from pprint import pprint
from ha_domain.ha_domain_stack import HaDomainStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ha_domain/ha_domain_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = HaDomainStack(app, "ha-domain")
    template = assertions.Template.from_stack(stack)

    t1 = app.synth().get_stack_by_name('ha-domain').template

    for resources in t1["Resources"]:
    #    print(t1["Resources"][resources]["Type"])
         pprint(t1["Resources"][resources]["Properties"])

    resources_count = {
        "AWS::Route53::HostedZone": 1,
        "AWS::ApiGateway::RestApi": 1,
        "AWS::IAM::Role": 2,
        "AWS::ApiGateway::Account": 1,
        "AWS::ApiGateway::Deployment": 1,
        "AWS::ApiGateway::Stage": 1,
        "AWS::ApiGateway::Resource": 1,
        "AWS::ApiGateway::Method": 1,
        "AWS::IAM::Policy": 1,
    }

    for kind, count in resources_count.items():
        assert (
                len(template.find_resources(kind)) == count
        ), f'There should be exactly {count} resources of type "{kind}"'


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
