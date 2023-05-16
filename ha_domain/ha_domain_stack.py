from aws_cdk import Stack

from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class HaDomainStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import HZ from SSM Param store
        hz_id = ssm.StringParameter.from_string_parameter_attributes(
            self, "hz_name", parameter_name="/ddns/hz_id"
        )

        api_role: iam.Role = iam.Role(
            self,
            "api_role",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
        )

        api_role.add_to_policy(
            iam.PolicyStatement(
                actions=["route53:ChangeResourceRecordSets"],
                resources=[f"arn:aws:route53:::hostedzone/{hz_id.string_value}"],
            ),
        )

        domain_name = "vpn.example.com"  # Set domain name here

        template_xml: str = f"""
<ChangeResourceRecordSetsRequest xmlns="https://route53.amazonaws.com/doc/2013-04-01/">
     <ChangeBatch>
         <Changes>
             <Change>
                 <Action>UPSERT</Action>
                 <ResourceRecordSet>
                     <Name>{domain_name}</Name>
                     <Type>A</Type>
                     <TTL>60</TTL>
                     <ResourceRecords>
                         <ResourceRecord>
                             <Value>$context.identity.sourceIp</Value>
                         </ResourceRecord>
                     </ResourceRecords>
                 </ResourceRecordSet>
             </Change>
         </Changes>
     </ChangeBatch>
 </ChangeResourceRecordSetsRequest>
         """

        def imported_api():
            imp_api = apigw.SpecRestApi(
                self,
                "ddns_import",
                deploy=True,
                endpoint_types=[apigw.EndpointType.REGIONAL],
                deploy_options=apigw.StageOptions(stage_name="v1"),
                api_definition=apigw.ApiDefinition.from_inline(
                    {
                        "openapi": "3.0.1",
                        "info": {
                            "title": "ddns_import",
                            "version": "2023-05-14T20:34:12Z",
                        },
                        "servers": [
                            {
                                "url": "https://u0j4lf3pfg.execute-api.eu-west-1.amazonaws.com/{basePath}",
                                "variables": {"basePath": {"default": "v1"}},
                            }
                        ],
                        "paths": {
                            "/{zone_id}": {
                                "get": {
                                    "parameters": [
                                        {
                                            "name": "zone_id",
                                            "in": "path",
                                            "required": True,
                                            "schema": {"type": "string"},
                                        }
                                    ],
                                    "responses": {
                                        "200": {
                                            "description": "200 response",
                                            "content": {
                                                "application/json": {
                                                    "schema": {
                                                        "$ref": "#/components/schemas/Empty"
                                                    }
                                                }
                                            },
                                        }
                                    },
                                    "security": [{"api_key": []}],
                                    "x-amazon-apigateway-integration": {
                                        "type": "aws",
                                        "credentials": api_role.role_arn,
                                        "httpMethod": "POST",
                                        "uri": "arn:aws:apigateway:eu-west-1:route53:path//2013-04-01/hostedzone/{hosted_zone_id}/rrset/",
                                        "responses": {"default": {"statusCode": "200"}},
                                        "requestParameters": {
                                            "integration.request.path.hosted_zone_id": "method.request.path.zone_id",
                                            "integration.request.header.Content-Type": "'application/xml'",
                                        },
                                        "requestTemplates": {
                                            "application/json": template_xml
                                        },
                                        "passthroughBehavior": "never",
                                    },
                                }
                            }
                        },
                        "components": {
                            "schemas": {
                                "Empty": {"title": "Empty Schema", "type": "object"}
                            },
                            "securitySchemes": {
                                "api_key": {
                                    "type": "apiKey",
                                    "name": "x-api-key",
                                    "in": "header",
                                }
                            },
                        },
                    }
                ),
            )

            usage_plan = imp_api.add_usage_plan(
                "dns_plan",
                throttle=apigw.ThrottleSettings(rate_limit=4, burst_limit=3),
                quota=apigw.QuotaSettings(limit=1000, period=apigw.Period.MONTH),
            )
            usage_plan.add_api_stage(stage=imp_api.deployment_stage)

            key = imp_api.add_api_key(
                "key_1",
                api_key_name="ddns_update_key",
            )
            usage_plan.add_api_key(key)

        imported_api()
