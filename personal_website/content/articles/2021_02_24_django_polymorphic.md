Title: Polymorphic models in Django
Date: 2021-02-24 10:00

While there are a few ways to approach inheritance database models in Django, the main advantage of using polymorphic models lies in their simplicity of use and speed of development. At Merixstudio we appreciate this handy solution and use it in a number of projects to facilitate the creation of concise database relationships in an easy-to-read, clean-code manner.

Everyone who had a go at object-oriented programming surely experienced the use of polymorphism mechanisms one way or the other. Typically, you would create a class that implements some level of abstraction and override the functions in classes inheriting from it, changing output based on the object type. What if we could do the same thing with Django models? Today we will learn how to perform such magic using two Django packages.

## Interesting use case example for polymorphic models

Before we jump into writing code, let’s go through a use case example. The project’s goal is to create an application for real estate agents to store information about the available purchases - what we want to keep there is the data regarding different types of real estate for sale. While some parameters will be shared between sold properties (title, price, description), some will be exclusive for a given type. A couple of examples include:

- General real estate information (e.g. price), which is universally necessary for real estate agents, should be present in all models,
- The floor parameter should be available for an apartment but it doesn’t make much sense to have it in a plot,
- The plot type parameter would be applicable for a plot but not so useful in apartment parameters.

In Django we have a couple of options to choose from when solving the problem of varied data parameters:

- We can store everything in one model with null information when an object doesn’t use the parameters that describe other objects,
- We may build an elaborate relationship between models,

Or… you guessed it!

- **Use polymorphic models!**

## Initial steps with Django REST Framework

This guide assumes that you have a Django Rest Framework (DRF) project up and running. If you do not know how to work with Django or DRF, see the following guides:

- [Getting started with Django](https://www.djangoproject.com/start/)
- [Django Rest Framework Quickstart](https://www.django-rest-framework.org/tutorial/quickstart/)

We will start by installing the required packages using the pip tool (you can also add this straight to the project requirements file):

```bash
pip install django-polymorphic django-rest-polymorphic
```

Now we need to add the polymorphic app into our Django `settings.py` file:

```python
INSTALLED_APPS = (
    ...
    “polymorphic”,
    “django.contrib.contenttypes”, # Add this, if you haven't already
    ...
)
```

And guess what… we are ready to make the magic happen!

## Creating polymorphic models

Now that we have everything we need to create some exceptional code, let’s dig right into it. We will start by creating the base model that will contain the general information about the real estate we want to sell. Then, go to your `models.py` file and add the following:

```python
from polymorphic.models import PolymorphicModel


class RealEstate(PolymorphicModel):
    title = CharField(max_length=255)
    price = DecimalField(max_digits=9, decimal_places=2)
    description = TextField()
```

Notice how **we inherit from a PolymorphicModel instead of the standard Django Model**.

Next, we will create models for specific properties that will inherit from the `RealEstate` polymorphic model we just created.

```python
class Flat(RealEstate):
    floor = PositiveSmallIntegerField(default=1)


class Plot(RealEstate):
    class PlotType(TextChoices):
        CONSTRUCTION = "construction"
        AGRICULTURAL = "agricultural"

    plot_type = CharField(max_length=12, choices=PlotType.choices)
```

This went fast - we created three useful models in a matter of seconds.

## REST a while and listen

Since we already have a data storage solution, now we can build some functionality around it. For this we will use the other `django-rest-polymorphic` package with DRF. It will allow us to use polymorphic models in a RESTful way, by providing endpoints to CRUD for model instances.

### Django-based polymorphic serializers

To create serializers for each of the child models, we will be using the default `ModelSerializer`. Note how the fields of the parent model are defined in each of the child models below:

```python
from rest_framework.serializers import ModelSerializer
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import Flat, Plot, RealEstate


class RealEstateSerializer(ModelSerializer):
    class Meta:
        model = RealEstate
        fields = ("title", "price", "description")


class FlatSerializer(ModelSerializer):
    class Meta:
        model = Flat
        fields = ("title", "price", "description", "floor")


class PlotSerializer(ModelSerializer):
    class Meta:
        model = Plot
        fields = ("title", "price", "description", "plot_type")
```

Now that we have created serializers for specific models, we will create a `PolymorphicSerializer` to connect them together: this is done by providing a dictionary, where the key is our model and the value will be the serializer. This dictionary is then passed into the `model_serializer_mapping` variable:

```python
class RealEstatePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        RealEstate: RealEstateSerializer,
        Flat: FlatSerializer,
        Plot: PlotSerializer
    }
```

### Views creation in Django

To create a view, we will be using the `ModelViewSet` that provides all the CRUD capabilities out of the box. As you can see below, the view doesn’t look different from other views you create in Django. We pass the base `RealEstate` objects to the queryset, along with passing the serializer we just created to the `serializer_class`.

```python
from rest_framework.viewsets import ModelViewSet
from .models import RealEstate
from .serializers import RealEstatePolymorphicSerializer


class RealEstateViewSet(ModelViewSet):
    queryset = RealEstate.objects.all()
    serializer_class = RealEstatePolymorphicSerializer
```

After adding some objects into the database, a GET request in the view will provide data in the following format (look at how the structure is defined by the `resourcetype` key):

```json
[
    {
        "id": 1,
        "title": "Generic Real Estate",
        "price": 200000,
        "description": "Lorem ipsum dolor",
        "resourcetype": "RealEstate"
    },
    {
        "id": 2,
        "title": "Flat Real Estate",
        "price": 100000,
        "description": "Lorem ipsum dolor",
        "floor": 3,
        "resourcetype": "Flat"
    },
    {
        "id": 3,
        "title": "Plot Real Estate",
        "price": 300000,
        "description": "Lorem ipsum dolor",
        "plot_type": "construction",
        "resourcetype": "Plot"
    }
]
```

## The admin panel

One way to work with the admin panel containing our models would be to simply register them like you normally would:

```python
admin.site.register(RealEstate)
admin.site.register(Flat)
admin.site.register(Plot)
```

While this would work just fine, it does not provide all the features that django-polymorphic gives us regarding the admin panel. The package provides a cohesive interface for polymorphic models, that allows us to display different child models on the same page, when connected with the parent model. It also provides an easy way to create new models in one place through the admin panel, with regard to the type of the model.

With that in mind, we will start by adding imports into our `admin.py` file:

```python
from django.contrib import admin
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicParentModelAdmin,
)
from .models import Flat, Plot, RealEstate
```

Let’s continue with creating the child and parent model admins. The `polymorphic_list` keyword will allow the admin to place all models under a single page (quite neat!).

```python
class FlatAdmin(PolymorphicChildModelAdmin):
    base_model = Flat

class PlotAdmin(PolymorphicChildModelAdmin):
    base_model = Plot

class RealEstateAdmin(PolymorphicParentModelAdmin):
    base_model = RealEstate
```

The last thing we need to do is to register the admins to our site:

```python
admin.site.register(Flat, FlatAdmin)
admin.site.register(Plot, PlotAdmin)
admin.site.register(RealEstate, RealEstateAdmin)
```

## Creating fixtures

What happens, if you want to use `django-polymorphic` to create some initial data for your project? As you probably noticed, the package uses Django content types to manage relationships between parent and child models. If you dump your data the standard way, you will get errors any time you change the model structure (`ContentType` objects are automatically created by Django during the database synchronization process). How can we deal with that problem? It is quite simple - by using **natural keys**.

```bash
python manage.py dumpdata --natural-foreign > project_data.json
```

Natural keys are a feature provided by Django for convenience. Instead of referring to an object by its ID field, a natural key provides a tuple of values to identify an object instance. This also allows you to load data into an existing database, when you can’t guarantee that the primary key is not already in use by another object. For more information please visit the [official documentation](https://docs.djangoproject.com/en/3.1/topics/serialization/#natural-keys).

## Are you ready for an adventure?

Today we created a simple application for real estate agents. While that wasn’t the most innovative product around, we learned how to easily bring polymorphism into the world of Django models. We only scratched the surface of what the Django packages have to offer, so if you are interested in learning more, be sure to click the below links we selected for you. Once you check them out, you will know that this is just the beginning of your adventure with polymorphism!

The official sources with more information about both packages:

- [django-polymorphic package](https://django-polymorphic.readthedocs.io/en/stable/quickstart.html)
- [django-rest-polymorphic package](https://github.com/denisorehovsky/django-rest-polymorphic)