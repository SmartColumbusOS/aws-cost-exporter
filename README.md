# Prometheus AWS Cost Exporter

### Description

This export will query AWS Cost Explorer API to export daily cost. Pushes the value to prometheus using the push gateway.

### Permissions
This requires AWS IAM permissions to query the cost explorer API in the root account.
This is currently done by assuming a role that was manually created in the root account.  

### Deploying to Sandbox

* This application can be deployed to the sandbox environment using the following Terraform commands:
  * `tf init`
  * `tf workspace new {NEW_WORKSPACE_NAME}`
  * `tf plan --var=file=variables/sandbox.tfvars --out=out.out`
  * `tf apply out.out`

### Visualizing AWS Costs

Once cost metrics have been exported to Prometheus, you can create create graphs to better visualize the your AWS costs over time.  See the [example grafana template](aws-cost-grafana-example.json) for guidance.
