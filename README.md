/getparams  

**POST**

Returns all params currently stored in the database.

*Requires*  
```
{
    "authToken" : "<auth token>",
    "userInfo" : {
        "userName" : "<user name>",
        "usereEmail" : "<user email>"
    }
}
```  
*Example response*  

```
[
    {
        "name" : "<app name>",
        "value" : "<parameter value>",
        "comment" : "<comment>",
        "secret" : <secret boolean>
    },
    ...
]
```  
---  
/getupdates  

**POST**

Returns all parameter updates stored in the updates table.  

*Requires*  
```
{
    "authToken" : "<auth token>",
    "userInfo" : {
        "userName" : "<user name>",
        "usereEmail" : "<user email>"
    }
}
```  
*Example response*  

```
[
  {
    "id": 1,
    "value": "<parameter value>",
    "comment": "<comment>",
    "useremail": "<user email>",
    "username": "<user name>",
    "name": "<app name>",
    "secret": <secret boolean>,
    "datetime": "<datetime string>"
  },
  ...
]
```  
--- 
/save  

**POST**

Saves new parameter to params table, creates an update entry. Returns a JSON string list of updates created.

*Requires*  
```
{
  "authToken": "<auth token>",
  "userInfo": {
    "userName": "<user name>",
    "userEmail": "<user email>"
  },
  "parameters": [{
    "name": "<app name>",
    "value": "<app value>",
    "secret": <secret boolean>,
    "comment": "<comment>"
    },
    ...
  ]
}

```
*Example Example response*  
```
[
  {
    "username": "<user name>",
    "useremail": "<user email>",
    "name": "<app name>",
    "value": "<app value>",
    "secret": <secret boolean>,
    "comment": "<comment>"
  },
  ...
]

```
--- 
/post  

**This endpoint is still a work in progress.**

Clone github repository, create new branch, save current state of params table to JSON file, push to github then create a pull request on github for created branch. Returns branch name.

**POST**  

---  
/store  

**This endpoint is still a work in progress.**

Update AWS Parameter store with the current state of all application parameters existing in the database at time of request.

**POST** 