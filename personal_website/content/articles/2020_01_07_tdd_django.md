Title: TDD for Django using pytest
Date: 2020-01-07 10:00

When applying to any IT company, you are often asked, if you know the magic term TDD. What is this? Let's find out! TDD stands for Test Driven Development and is one of the fundamental philosophies of sofware creation. Let's see what wikipedia tells about it:

> Test-driven development (TDD) is a software development process that relies on the repetition of a very short development cycle: requirements are turned into very specific test cases, then the software is improved so that the tests pass. This is opposed to software development that allows software to be added that is not proven to meet requirements.

That sounds cool, so basically we get a working application, with features working as requested... already when we finish writing the code! That's pretty awesome. So, what steps do we need to take, to write a TDD project?

1. Get the requirements for your new feature - they need to be described very well (preferably using user stories), so that you exactly know what your function/endpoint/process should do.
2. Write tests that will check everything described in the feature (what it should return, how values are calculated, etc).
3. Run the tests, if all new tests failed, you are on a good road to be a TDD master.
4. Write your awesome code, that will implement the feature.
5. Run tests again. If they fail, go to point 4, otherwise good job! You have implemented your feature and are considered a top programmer in your team.
6. Refactoring is always a good idea, no one writes perfect code on their first try. So go through your code and see, what can be improved. It's always good to run tests again after this step to see, if you didn't crash your code on the way.

## Why pytest?

`pytest` provides a new approach for writing tests, giving you a couple of neat things and helpers:

- Assert statements (you don't need to use `self.assert` anymore),
- Great information why exactly your test failed,
- You have more control over Fixtures,
- Test modules are auto-discovered,
- Parametrizing, so you can run multiple tests at once,
- Less boilerplate,
- A lot... and I mean a lot... of pytest external plugins,
- And many more.

## Installing pytest

To install pytest, we will use the pip command tool. Notice that we aren't installing the base module `pytest`, but rather the wrapper for django called `pytest-django` (the base module will be installed alongside). The only thing you need to write the following line in your desired environment:

```bash
pip install pytest-django
```

You can optionally check, if you installed the correct version:

```bash
pytest --version
```

## Using pytest in your django project

First of all, we need to tell Django, that we will use pytest in our project. To do that, create a `pytest.ini` file inside the root directory. Fill it in with the following code (of course replace `project_name` with your project name):

```
[pytest]
DJANGO_SETTINGS_MODULE = project_name.settings
```

You can also specify the settings file as an environment variable, which is considered a good practice and allows easy setting switching. Moreover, if you are using non-standard test file names (specific files or wildcard), you can add the following line:

```
python_files = test.py test_*.py *_test.py
```

To run your tests, you won't use `manage.py` as you did with the `unittest` library. Now it's a bit more simple, the default command is: `pytest`.

If you want to run a specific directory, file or function, you can do that as well! Just run one of the following, replacing names with what you got:

```
pytest some_directory
pytest some_file.py
pytest some_file.py::your_function
```

## Where to place tests?

In theory... anywhere you want. In practice, it is good to place them inside the `tests` directory of your Django Application. This way, each application has their own project space to keep tests in. Moreover, you can (and should) divide tests into files, depending what they are testing, as an exampe:

- `test_api.py` - to test endpoints, and what is returned,
- `test_services.py` - to test external services or bigger things in your project,
- `test_models.py` - to test models,
- and so on.

This is really up to your preference, but it is good to keep one pattern over the entire project.

## Writing great API tests

I think we can start building our test suite for a project we are doing. Consider having a model `Animal` that is part of the application `zoo`, the model has two fields `name` and `age`. I'm going to write a test for a function that checks, whether the model is saved correctly, when we run the endpoint on our django API.

```python
# First, let's import pytest
import pytest

# Import a model (you need to import yours)
from zoo.models import Animal

# Write a cool test function
# We will use an authorized client fixture for that
def test__add_animal(authorized_client):
    # This is the data we want to save in the model
    data_to_save = {
        'name': 'Wifi',
        'age': 4,
    }

    # Let's assume our endpoint looks like this:
    # POST localhost:8080/api/animals
    url = reverse('api:animals')

    # Time to send the data
    response = authorized_client.post(
        url,
        data_to_save,
        content_type='application/json',
    )

    # Let's check if the request was successful
    assert response.status_code == 200

    # Does the response json match what we posted?
    assert response.json() == data_to_save

    # Let's see if the object was added
    all_animals = Animal.objects.all()
    assert all_animals.count() == 1

    # Check, if the object is exactly like the one we wanted to save
    saved_animal = all_animals.first()
    assert saved_animal.name == 'Wifi'
    assert saved_animal.age == 4
```

## Writing great unit tests

ut sometimes you have a more complicated endpoint than this, and you create additional service functions, that calculate things, gather data from external sources or anything else. It would be good to separate those tests for structure. Let's assume we have a really cool function that gathers animal quantity over land from an external API. We have a function `get_quantity_from_external` that takes the response, and returns a value for `quantity`.

```python
# Again, let's import pytest
import pytest

# Import our function
from zoo.services import get_quantity_from_external

# Notice that here we are patching the external data
# We are doing this to mock the external service
# So it's not called each time we test

@patch('zoo.services.external_function')
def test__get_quantity_from_function(
    external_function,  
):
    # First let's mock the response from external sources
    # The data is taken from National Geographic
    external_function.return_value = [
        {
            'animal': 'Great Elephant',
            'quantity': 352271,
            'region': 'Africa',
            'specie_range': 0.93,
        },
    ]

    # Time to call and assert our function!
    result = get_quantity_from_external('Great Elephant', 'Africa')
    assert result == 352271
    assert isinstance(result, int)

    # Let's check, if the function returns None when not in db
    # Thanks C.S.Lewis for this
    result = get_quantity_from_external('Hnakra', 'Mars') 
    assert result == None
```

## Summary

Today we learned a few things. How to install pytest (and why it is so awesome), how to setup your django project and run it, how to structure your project regarding tests and how to write integration and unit tests with examples. Of course this isn't the whole topic, but gives you a nice introduction to what is to come. For more information, you should really check the official website for pytest Documentation.

Happy testing!
