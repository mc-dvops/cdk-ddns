
# A Dynamic DNS on AWS done via CDK and Python

A CDK stack to create a Dynamic DNS address, so I can reliably connect to my home network.

So I was looking to setup a Dynamic DNS, did some googling and found a [very nice guide](https://docs.rackspace.com/blog/how-to-create-a-dynamic-dns-with-the-aws-api-and-route-53/) using Route53 and API Gateway on AWS.
Seeing as I already had a domain name and hosted zone on AWS, this was exactly what I needed.

Got it up and running, all good, so then decided I'd move this to CDK, it'll take an hour or so and it'll be there for easy re-deployment - boy was I wrong. The initial CDK setup was simple, got the gateway, resource and methods defined - `cdk synth` succeeded, but `cdk deploy` failed due to an invalid method in the integration request. For some reason the **Integration Request** could not access the **Method Request** methods.

### Ok, problem solving time:
- Compared the manual and CDK stacks in the GUI - no visible difference, but integration could see the method request (in the manually deployed stack)
- Made various changes to the stack
- Deployed the stack with less parts and then manually adding the remaining parts
- Started working with L2 constructs, so switched to using L1 constructs
- Many hours later, still not able to get it working, 

Then I stumbled across an answer on [SO](https://stackoverflow.com/questions/70897136/api-gateway-canned-response-from-get-request) to a question about API Gateway CloudFormation which suggested manually standing up the API Gateway, exporting the spec file and using that in CDK for a new stack.
I added the spec inline, but it can be imported from a file.

###     Few more changes were needed:

- Set Deploy=True and set the stage name via DeploymentOptions - needed for adding the usageplan/API Key
- Set the API Endpoint type
- Added usage plan
- Added API Key
- Updated the API spec so the Servers -> Variable -> basePath to match the stage name

This stack assumes you have already deployed a hosted zone, and stored the HZ ID in the Parameter Store under the name **/ddns/hz_id**. 
This value could be easily added as a string instead.

The API endpoint will be displayed as part of the synth output.
The api-key can be seen on the GUI or via cli


To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
