# Advanced cloud deployments

## A. Deploying on an AWS EC2 Instance

This guide will walkthrough how to deploy ***Synergos UI*** using ***AWS Console***.

1. Create an allocated VM instance in your AWS console. Detailed instructions on how to this can be found [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html). 

    To start off, click **`"Launch Instance"`**.

    ![Launching your instance 1a](/docs/images/deployment/synui_deployment_aws_step1a_final.png)

2. Before you can launch a VM, you need to configure it. 

    ![Launching your instance 1b](/docs/images/deployment/synui_deployment_aws_step1b_final.png)

    1. Name your instance.
    2. Select your instance's OS.
    3. Make sure that you are using a **stable** linux version and that architecture is set to `"64-bit(x86)"`

    ![Launching your instance 1c](/docs/images/deployment/synui_deployment_aws_step1c_final.png)

    4. Select an appropriate instance type for your usecase.
        - Heavy user traffic: Allocate more compute
        - Low user traffic: Allocate less compute

    5. Ensure that ***HTTP*** & ***HTTPS*** traffic is allowed.

    ![Launching your instance 1d](/docs/images/deployment/synui_deployment_aws_step1d_final.png)

    6. Set an appropriate amount of storage (Recommended: `~30GB`).
    7. Finalize these configurations by clicking on **`"Launch Instance"`**. 

3. Once your instance has been successfully deployed, you will be able to check its networking details from the **`"Instances"`** dashboard. 

    Take note of your instance's `<Public IP address>`.

    ![Configure your security 2a](/docs/images/deployment/synui_deployment_aws_step2a_final.png)

4. Explore the instance's **`"Security"`** details. Your VM instance will be automatically allocated a default security group `<xxx (launch-wizard-y)>`. Click on it to navigate to its configuration page.

    ![Configure your security 2b](/docs/images/deployment/synui_deployment_aws_step2b_final.png)

5. ***Synergos UI*** uses 3 main ports for navigation, viewing & tracking services. Hence, you will need to configure your firewall settings to expose these ports for use.

    1. Click **`"Edit inbound rules"`** to add new port definitions.

        ![Configure your security 2c](/docs/images/deployment/synui_deployment_aws_step2c_final.png)

    2. By default, ***Synergos UI*** services uses ports `4000`, `4001` & `4002`. Add these definitions to your inbound rules as seen below.

        ![Configure your security 2d](/docs/images/deployment/synui_deployment_aws_step2d_final.png)

    3. Click `"Save rules"`.

6. Double check that your new definitions have taken effect.

    - Your new rules should be visible in the security group `<xxx (launch-wizard-y)>`'s inbound rules.

        ![Configure your security 2e](/docs/images/deployment/synui_deployment_aws_step2e_final.png)

    - Your new rules should be visible in your instance's **`"Security"`** details. 

        ![Configure your security 2f](/docs/images/deployment/synui_deployment_aws_step2f_final.png)

7. Connect into your remote command prompt. Detailed instructions can be found [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstances.html). 

    Once you have set up your security key, run the following command in your terminal.

    ```
    ssh -i <your security key>.pem ubuntu@<Public IP address>
    ```

8. Install **`Docker`** into your VM instance. Detailed instructions can be found [here](https://docs.docker.com/engine/install/ubuntu/). 

    > Alternatively, you can launch your AWS instance with Docker pre-installed using "Ubuntu with Docker" image. However, this option has its own set of financial considerations for maintanence.  

9. With your VM instance properly configured, you are ready to run ***Synergos UI***. 

    Execute the following commands:

    ```
    # Download source repository
    git clone https://github.com/aimakerspace/synergos_ui
    cd ./synergos_ui

    # Initialize & update all submodules
    git submodule update --init --recursive
    git submodule update --recursive --remote

    # Grant permissions to execute deployment script
    chmod +x ./scripts/deploy_aws.sh

    # Execute deployment
    [sudo] ./scripts/deploy_aws.sh
    ```

---

## B. Deploying on an GCP Cloud Compute Instance

[Coming soon!]