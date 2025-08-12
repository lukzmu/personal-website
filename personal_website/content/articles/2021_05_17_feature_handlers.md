Title: Providing feature handlers in an elegant way in Python
Date: 2021-05-17 10:00

Lately one of my colleagues has shown me a neat way of providing functional handlers, instead of working with an **if-elif-else** structure. I liked it so much that not only did I implement it with some pieces of my code, but also decided to share the method with you in this blog post!

Today we will create handlers and a provider that will take care of email sending in a data import process based on two custom model fields:

- `ImportConfiguration.notifications`,
- `ImportStatus.status`.

You can preview how the fields are defined in the models below:

```python
class ImportConfiguration(Model):
    class ImportNotification(TextChoices):
        NONE = "none", _("Don't notify me")
        FINISHED = "finished", _("Notify me when finished")
        ERRORS = "errors", _("Notify me when errors detected")

    notifications = CharField(
        max_length=8,
        choices=ImportNotification.choices,
        default=ImportNotification.ERRORS,
    )


class ImportStatus(Model):
    class Status(TextChoices):
        AWAITING = "awaiting", _("Awaiting")
        IN_PROGRESS = "in_progress", _("In progress")
        COMPLETE = "complete", _("Complete")
        COMPLETE_WITH_ERRORS = "complete_with_errors", _("Complete with errors")
        FAILED = "failed", _("Failed")

    status = CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AWAITING,
    )
    import_configuration = ForeignKey(ImportConfiguration, on_delete=PROTECT)
```

The user can set 3 notification settings in the import configuration:

- `NONE`, which won't send emails at all for this import,
- `FINISHED`, which will send an email when the import has been finished,
- `ERRORS`, which will send an email when import errors occur.

After the import has been finished, you might end up with 3 possible statuses:

- `COMPLETE`, when everything goes as planned, with no errors occurring during the import.
- `COMPLETE_WITH_ERRORS`, when the import is fine, just some items are corrupted,
- `FAILED`, when everything blows up.

## Creating the handler

Let's start by declaring an abstract class that will describe our email handlers. I will call it `ImportEmailHandler` (notice the use of `ABC` from the `abc` package). We will also declare the following constant values:

- `_SENDER` is the value that will be used as the email sender,
- `_SUBJECT` will be the value for the email topic,
- `_TEMPLATE` will be the template file for the email,
- `_TEMPLATE_TXT` the template for text emails (when someone doesn't support HTML messages).

```python
class ImportEmailHandler(ABC):
    _SENDER = "contact@merixstudio.com"
    _SUBJECT: Optional[str] = None
    _TEMPLATE: Optional[str] = None
    _TEMPLATE_TXT: Optional[str] = None
```

The handler will provide one public function - `send`. The goal of this function is to prepare an email message based on the `ImportStatus` context and then send it to the user.

```python
class ImportEmailHandler(ABC):
    ...

    @classmethod
    def send(cls, import_status: ImportStatus):
        message, html_message = cls._prepare_messages(import_status=import_status)
        recipients = cls._get_recipients(user=import_status.user)

        if recipients:
            send_mail(
                subject=cls._SUBJECT,
                message=message,
                html_message=html_message,
                from_email=cls._SENDER,
                recipient_list=recipients,
                fail_silently=True,
            )
```

As you can see, the `send` function uses two class methods:

- `_prepare_messages` will build the messages from the provided template and import context,
- `_get_recipients` which will gather a list of emails, to which the message should be delivered.

```python
class ImportEmailHandler(ABC):
    ...

    @classmethod
    def _prepare_message(cls, import_status: ImportStatus) -> Tuple[str, str]:
        assert cls._TEMPLATE is not None
        assert cls._TEMPLATE_TXT is not None
        assert cls._SUBJECT is not None

        template = get_template(cls._TEMPLATE_TXT)
        html_template = get_template(cls._TEMPLATE)
        context = cls._get_context(import_status=import_status)
        return template.render(context), html_template.render(context)

    @classmethod
    def _get_recipients(cls, user: CustomUser) -> List[str]:
        # Write your logic to gather email list
        return ["l.zmudzinski@merixstudio.com"]
```

We also have one more crucial function in the class - the `_get_context`. This is an abstract method that should be used in any derivative class of the `ImportEmailHandler`. Its function is to provide context for email templates.

```python
class ImportEmailHandler(ABC):
    ...

    @classmethod
    @abstractmethod
    def _get_context(cls, import_status: ImportStatus) -> Dict[str, Any]:
        pass
```

### Example of implementation

Let's implement a `CompletedEmailHandler` to be used when the notifications are set to `FINISHED` and the status is `COMPLETE`. Let’s see how easy it is to define the handler for this specific case.

```python
class CompletedEmailHandler(ImportEmailHandler):
    _SUBJECT = "The import has completed"
    _TEMPLATE = "email/completed.html"
    _TEMPLATE_TXT = "email/completed.txt"

    @classmethod
    def _get_context(cls, import_status: ImportStatus) -> Dict[str, Any]:
        # The dictionary keys depend on your template
        return {
            "message": "Your import has completed!",
            "status": import_status.status,
        }
```

## Provider creation

Now that we have a way to define handlers, we need a provision method suitable to our situation. Let's create an `ImportEmailHandlerProvider` class! It will have one private variable field called `_handlers`, as is shown below:

```python
class ImportEmailHandlerProvider:
    def __init__(self):
        self._handlers: Dict[
            ImportConfiguration.ImportNotification,
            Dict[ImportStatus.Status, Type[ImportEmailHandler]],
        ] = defaultdict(dict)
```

To register new handlers based on notification and status values, we will create a new public function register, which basically adds handlers to the dictionary.

```python
class ImportEmailHandlerProvider:
    ...

    def register(
        self,
        notification: TextChoices,
        status: TextChoices,
        handler: Type[ImportEmailHandler],
    ) -> ImportEmailHandlerProvider:
        self._handlers[notification][status] = handler
        return self
```

And another one to retrieve the registered handlers:

```python
class ImportEmailHandlerProvider:
    ...

    def get(
        self,
        notification: ImportConfiguration.ImportNotification,
        status: ImportStatus.Status,
    ) -> Type[ImportEmailHandler]:
        try:
            return self._handlers[notification][status]
        except KeyError as cause:
            raise ImportEmailHandlerNotFoundError(
                notification=notification, status=status,
            ) from cause
```

However, as you can see, we should raise `ImportEmailHandlerNotFoundError` when we are not able to provide a handler. This is a custom exception defined in the `exceptions.py` file that should be handled in your code in some way (depending on what you want to do with this fact).

```python
class ImportEmailHandlerNotFoundError(Exception):
    def __init__(
        self,
        notification: ImportConfiguration.ImportNotification,
        status: ImportStatus.Status,
    ):
        super().__init__(
            f"Email import handler for notification '{notification} and "
            f"status '{status}' not found."
        )
```

### Registering email handlers

Now that we have a class that will store and provide handlers for us - we just need to define which handler should be returned depending on the field parameters. Take a look below - this is how we can do it:

```python
import_email_provider = (
    ImportEmailHandlerProvider()
    .register(
        notification=ImportConfiguration.ImportNotification.FINISHED,
        status=ImportStatus.Status.COMPLETE,
        handler=CompletedEmailHandler,
    )
    .register(
        notification=ImportConfiguration.ImportNotification.FINISHED,
        status=ImportStatus.Status.COMPLETE_WITH_ERRORS,
        handler=ErrorEmailHandler,
    )
    .register(
        notification=ImportConfiguration.ImportNotification.FINISHED,
        status=ImportStatus.Status.FAILED,
        handler=FailedEmailHandler,
    )
    .register(
        notification=ImportConfiguration.ImportNotification.ERRORS,
        status=ImportStatus.Status.COMPLETE_WITH_ERRORS,
        handler=ErrorEmailHandler,
    )
    .register(
        notification=ImportConfiguration.ImportNotification.ERRORS,
        status=ImportStatus.Status.FAILED,
        handler=FailedEmailHandler,
    )
)
```

The only thing left is to send the email at the end of the import process:

```python
def send_email(import_status: ImportStatus):
    # We will start by retrieving the handler
    handler = import_email_provider.get(
        notification=import_status.import_configuration.notifications,
        status=import_status.status,
    )

    # And now we can send the message!
    handler.send(import_status=import_status)
```

After doing it yourself, I am sure you will be inclined to say that using the described handler-provider method is a great (much more readable) alternative to the standard use of **if-elif-else** structure, which you can see below:

```python
def send_email(import_status: ImportStatus):
    if (
        import_status.status == ImportStatus.Status.COMPLETE
        and import_status.import_configuration.notifications
        == ImportConfiguration.ImportNotification.FINISHED
    ):
        handler = CompletedEmailHandler
    elif (
        import_status.status == ImportStatus.Status.COMPLETE
        and import_status.import_configuration.notifications
        == ImportConfiguration.ImportNotification.FINISHED
    ):
        handler = ErrorEmailHandler
    elif (
        import_status.status == ImportStatus.Status.COMPLETE
        and import_status.import_configuration.notifications
        == ImportConfiguration.ImportNotification.FINISHED
    ):
        handler = FailedEmailHandler
    elif (
        import_status.status == ImportStatus.Status.COMPLETE
        and import_status.import_configuration.notifications
        == ImportConfiguration.ImportNotification.FINISHED
    ):
        handler = ErrorEmailHandler
    elif (
        import_status.status == ImportStatus.Status.COMPLETE
        and import_status.import_configuration.notifications
        == ImportConfiguration.ImportNotification.FINISHED
    ):
        handler = FailedEmailHandler
    else:
        raise ImportEmailHandlerNotFoundError

    handler.send(import_status=import_status)
```

That's all Folks!

## Up to try it yourself?

Summing up, in this article we showed you a viable alternative to using the if-elif-else structure for providing functional handlers in your Python-based projects. The handler-provider method that we explained here ensures better code intelligibility, making handler and provider creation easier. A way to go, isn’t it?