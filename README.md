git # merchant-working-capital-back

## Setup

You need create a **.env** file with all environment variables used in the project 
only copy the file **.env.dist** and delete the **.dist** in the file name and fill the values.

**Project structure**
```
Backend
└─ src                          <---- project code.
└─ templates                    <---- Cloud formation template for depliy the prohect (cloudformation).
└─ utils                        <---- Template for create new lambdas in the project.
└─ .env.dist                    <---- Never delete this file, use only like template.
└─ .env                         <---- File with all environment variables used in the project.
└─ .flake8                      <---- Flake configuration.
└─ .gitignore                   <---- A simple gitignore.
└─ .pre-commit-config.yaml      <---- basic configuration of precommit.
└─ README.md                    <---- Basic dicumentation.
└─ requirements.txt             <---- Development requirements.

```

In the project folder run:

```commandline
.\venv\Scripts\activate
pip install -r requirements.txt
apm project install
```

## Lambdas

### Create a simple new lambd

```commandline
apm lambda new --name [lambda name]
```

### Create a new lambda with endpoint.

```commandline
apm endpoint new --name [lambda name] --endpoint [endpoint path] --verb [get|put|post|path|delete]
```

### Create a new lambda with endpoint and cors

```commandline
apm endpoint new --name [lambda name] --endpoint [endpoint path] --verb [get|put|post|path|delete] --cors
```

The commands above makes a folder in .src/lambdas/[lambda-name] with the next structure

```
Backend
│
└───src
│   │
│   └───lambdas
│   │   │
│   │   └───[lambda-name]
│   │   │   │   __init__.py
│   │   │   │   configuration.json
│   │   │   │   lambda_function.py
│   │   │   │   test_lambda_function.py
│   │   │   │

---------------------------------------------------------------------
__init__.py             --> Only used for mark folder like module.
configuration.json      --> Here is all configuration for the lambda.
lambda_function.py      --> Here is the code for the lambda.
test_lambda_function.py --> Here is the test for the lambda.
```

### Add endpoint to existent lambda

```commandline
apm endpoint add --lambda-name [lambda name] --endpoint [endpoint path] --verb [get|put|post|path|delete]
```

### Rename lambda

```commandline
apm lambda rename --name [actual-name] --new-name [new-name]
```

### Rename Endpoint

```commandline
apm endpoint rename --lambda-name [lambda-name] --new-endpoint-name [new-endpoint name]
```

### Show all lambdas in the project

```commandline
apm lambda list
```

### Show all endpoints in the project

```commandline
apm endpoint list
```

### delete a lambda

```commandline
apm lambda delete --name [lambda-name]
```

### delete only the endpoint

```commandline
apm endpoint delete --name [lambda-name]
```
