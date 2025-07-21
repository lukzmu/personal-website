Title: How to use FastAPI for microservices
Date: 2021-11-18 10:00

For the last couple of years, we could see a trend in the IT industry of moving away from monolith applications to microservices. Today we will describe the idea behind the movement, outline pros and cons of the approach and show how to work with microservices using the FastAPI Python framework.

Ready? Let’s go then!

## Microservices. How do they work?

The microservice architecture brings the idea of **decoupling functional parts of software applications into lightweight, deployable solutions, each having its own goal in the general ecosystem**. The approach has been adopted by many leading companies (e.g. Netflix, Amazon, Apple) and is well suited for any business that wants to adopt an Agile approach to software production.

Let's describe some key features of the microservice architecture:

1. **Multiple components**
    - Each service is a standalone component of its own,
    - Components’ deployment, replacing and removal is possible without compromising other services,
    - You have a relatively explicit component interface without tight data coupling.
2. **Business-oriented**
    - The services are built around business context and needs,
    - Each microservice is a product of its own,
    - Microservices necessitate having cross-functional teams that manage their respective products.
3. **Smart connection**
    - The services are usually connected by simple, ‘smart’ HTTP requests,
    - The information flows through [dumb pipelines](https://martinfowler.com/articles/microservices.html#SmartEndpointsAndDumbPipes).
4. **Decentralize everything**
    - Each service has its own resources and data storages,
    - Naming decisions can be different across the system,
    - You need to implement [Data Transfer Objects](https://martinfowler.com/eaaCatalog/dataTransferObject.html) (DTOs) for communication.
5. **Let it fail**
    - Microservices must acknowledge that other services may fail,
    - Service failure is common due to availability issues triggered by, for example, connection problems, server downtime, and the like.

You can often use an additional architectural layer in the form of an API Gateway to simplify the connections that client applications need to make to gather data from the system.

There are downsides to this approach. So, keep in mind, that API Gateways can:

- Increase response times for client requests,
- Become a bottleneck, if not scaled properly,
- Add another point of (possible) failure,
- Increase maintenance costs.

## Should I implement microservices? Pros and Cons.

As we’ve already learned what [microservices](https://www.merixstudio.com/blog/microservices-nodejs-moleculer/) are, we should  also discuss the positive and negative effects of choosing this type of [architecture for your project](https://content.merixstudio.com/insights/how-choose-right-cloud-architecture-your-business/?theme=how%20we%20work). You can treat the following table as a "cheat sheet" for selecting the right architectural setup for your next product.

| **Positives** | **Negatives** |
| :--- | :--- |
| Each service can run on its own | Latency in communication between services to get an end response |
| Less development time due to services modularity | Testing between multiple microservices can be a challenge |
| Infrastructure scaling depends on individual services | The cost of supporting multiple instances can scale up quickly |
| Easier to add new features or disable the existing ones | Information barriers due to additional layer of data provisioning | 
| The code is organized by business logic | Some use cases can span across multiple services |
| Independence from the old code stack | Support for multiple code stacks in one system |
| Awesome failure isolation | Additional work needed to create DTOs and failure mechanisms |

## The FastAPI implementation of microservices

Now that we know the theory behind microservices, we are ready to create an application that will use the architecture to provide some information to the user. We will use the aforementioned FastAPI to achieve this goal.

### But wait... what is FastAPI?

I'm glad that you asked! Let's see what we can read about it on the framework’s official website:

> FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

The framework's official website mentions a number of pros of FastAPI. In my opinion, the most useful features from a microservice perspective are: the simplicity of code (easy to use and avoid boilerplate), high operational capacity thanks to [Starlette](https://www.starlette.io/) and [Pydantic](https://pydantic-docs.helpmanual.io/) and compatibility with industry standards - [OpenAPI](https://swagger.io/specification/) and [JSON Schema](https://json-schema.org/).

### Don't we have Flask for that?

While both frameworks are great for creating APIs, FastAPI has a few crucial advantages over [Flask](https://www.merixstudio.com/blog/flask-vs-django-choosing-python-framework/):

- Easier views declaration,
- Out-of-the-box data validation,
- FastAPI error messages are displayed in a JSON format by default,
- It supports asynchronous tasks through [ASGI](https://asgi.readthedocs.io/en/latest/).

As FastAPI is a much younger framework, it implemented many today's standards for API creation, becoming the cool kid on the block in coding communities, and quickly growing in popularity.

### Installing FastAPI

You can install FastAPI using the pip tool:

```bash
pip install fastapi
```

To run the server, you will also need to install [Uvicorn](https://www.uvicorn.org/):

```bash
pip install "uvicorn[standard]"
```

And that is everything! We are ready to write our first microservice using FastAPI.

### Problem definition

We will create two simple services:

- An `auth_service` that will check whether the provided token is correct,
- An `information_service` that will provide the answer to all your questions.

Mind that both services will be super simplified, just to show the theory in practice. If you want to learn how to properly implement authentication in FastAPI, please refer to [this tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).

### Creation of the auth service

Let's start by creating the `auth_service.py` file and adding imports needed for the code to work:

```python
from typing import Optional

from fastapi import FastAPI, Header, Response
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
```

Now create the FastAPI application:

```python
app = FastAPI()
```

All we need to code is the **POST login** view. The response of the view will depend on the `Authorization` value in the header. This will provide us with two possible outcomes:

- `OK`, if the `Authorization` header has the value `"merixstudio"`,
- `UNAUTHORIZED`, in any other case.

```python
@app.post("/login/")
def login(
    authorization: Optional[str] = Header(None)
) -> Response:
    if not authorization == "merixstudio":
        return Response(status_code=HTTP_401_UNAUTHORIZED)
    return Response(status_code=HTTP_200_OK)
```

Using Uvicorn, we can start our service on port 8001:

```bash
uvicorn auth_service:app --reload --port 8001
```

### Information service creation

Now that we have our auth service up and running, we can create the information service. Create `info_service.py` and add the following imports:

```python
from functools import wraps
from typing import Any, Callable, Optional

import requests
from fastapi import FastAPI, Header, Response
from fastapi.responses import JSONResponse
```

Again, we will create the FastAPI application.

```python
app = FastAPI()
```

We need to define the endpoint we will contact in the `auth_service`:

```python
LOGIN_ENDPOINT = "http://127.0.0.1:8001/login/"
```

Now, we will write a custom Python decorator, that will contact the `auth_service`, check whether the user can be authorized and throw an exception, if they can’t. When no error is present, the endpoint will run normally.

```python
def auth_required(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        try:
            response = requests.post(
                url=LOGIN_ENDPOINT,
                headers={
                    "Authorization": kwargs["authorization"],
                },
            )
            response.raise_for_status()
            return func(*args, **kwargs)
        except requests.HTTPError as error:
            return Response(
                status_code=error.response.status_code
            )

    return wrapper
```

We can define the information endpoint right now, with all the answers you need. Mind the `@auth_required` decorator we created just a moment ago:

```python
@app.get("/info/")
@auth_required
def get_information(
    authorization: Optional[str] = Header(None)
) -> JSONResponse:
    return JSONResponse(content={"info": "The answer is 42."})
```

We can start this service on port 8000, using Uvicorn again:

```bash
uvicorn auth_service:app --reload --port 8000
```

### Running the microservices together

We will use `curl` to make some requests to the API. Let's start with no headers at all:

```bash
>> curl http://127.0.0.1:8000/info/ -i
HTTP/1.1 401 Unauthorized
```

As you can see, we got the **401 Unauthorized** status, that was transferred from the `auth_service`. If we pass a correct header, we will get the following response:

```bash
>> curl http://127.0.0.1:8000/info/ -i --header "Authorization: merixstudio"
HTTP/1.1 200 OK
{"info":"The answer is 42."}
```

It works! Great!

## Conclusions

In today's blog post we learned what microservices are. We talked about the pros and cons of using the microservices-based architecture in your projects. In recent years many big companies have used the microservice architecture in their products with success: Amazon, Netflix, Uber, Spotify... or OLX from the Polish playground. This trend will probably continue, as more companies move their infrastructure to the cloud. Serverless microservices can be a big deal for the future of backend software development.