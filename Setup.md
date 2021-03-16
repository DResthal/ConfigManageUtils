# Setup for ConfigApi  

1. First off, awscli will need to be installed and configured.  
```pip install awscli```  
Then run  
```aws configure```  
and follow the prompts to complete the configuration.   
Also be sure to add the TargetKeyId for your service and identity in the .env file (NOT .env.example)  
  
  
2. Second, a github access token will need to be generated.  
Login to Github then go to settings > Developer Settings > Personal access tokens > Generate new token. Give your token a name then select the "repo" checkbox which will in turn select all relevant chckboxes below. This allows access to private repositories, now Generate token at the bottom of the page.  
Be sure to copy your new access token and paste it into the .env file. Once you leave this page, you will not be able to return and see the access token and will need to delete it and generate a new one. 

3. Add your respective repository uris to the .env file. This is the https clone uri that Github gives you when you select the "code" button to clone the url. Please remove "https://" from your uri. For example, "github.com/DralrinResthal/ConfigManageUtils.git" instead of "https://github.com/DralrinResthal/ConfigManageUtils.git"

4. Add your own AUTH_TOKEN for authentication in the .env file. This could be anything, but the front end will need to send the exact same string and your AUTH_TOKEN in order to successfully authenticate with endpoints.
