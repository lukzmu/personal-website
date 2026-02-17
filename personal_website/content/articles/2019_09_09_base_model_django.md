Title: Creating a Base Model in Django
Date: 2019-09-09 10:00

When building a database for your application you sometimes need specific fields across all (or a great deal of) your models. It is a good practice to include creation time and update time fields, so you can see what changed… and when. Today we will go through the code needed to implement a base model for your database containing such data.

In our main application (named like your project, I named it `notes_api`) let’s create a new file: `models.py` (just like you would do in other django apps) and add the following code. The `abstract = True` line tells Django, that this shouldn’t be created as a model in the database. Moreover we can add some `ordering` so this is easier to use.

```python
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ['created_at']
```

Let’s consider now having a `Note` model somewhere in our Django system. Instead of adding the `created_at` and `updated_at` fields to each model, we can now use our freshly created `BaseModel` to do that for us:

```python
from django.db import models
from notes_api.models import BaseModel


class Note(BaseModel):
    description = models.CharField(
        max_length=255,
    )
```

Now, if we look at the model in the database, it will consists of 3 fields: The note description, the time at which it was created and the last update time.
