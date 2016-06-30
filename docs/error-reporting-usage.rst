Using the API
=============


Authentication and Configuration
--------------------------------

- For an overview of authentication in ``gcloud-python``,
  see :doc:`gcloud-auth`.

- In addition to any authentication configuration, you should also set the
  :envvar:`GCLOUD_PROJECT` environment variable for the project you'd like
  to interact with. If you are Google App Engine or Google Compute Engine
  this will be detected automatically.

- After configuring your environment, create a
  :class:`Client <gcloud.logging.client.Client>`

  .. doctest::

     >>> from gcloud import error_reporting
     >>> client = error_reporting.Client()

  or pass in ``credentials`` and ``project`` explicitly

  .. doctest::

     >>> from gcloud import error_reporting
     >>> client = error_reporting.Client(project='my-project', credentials=creds)

  Error Reporting associates errors with a service, which is an identifier for an executable,
  App Engine module, or job. The default service is "python", but a default can be specified
  for the client on construction time. You can also optionally specify a version for that service,
  which defaults to "default."


    .. doctest::

       >>> from gcloud import error_reporting
       >>> client = error_reporting.Client(project='my-project',
       ...                                 service="login_service",
       ...                                 version="0.1.0")

Reporting an exception
-----------------------

Report a stacktrace to Stackdriver Error Reporting after an exception

.. doctest::

   >>> from gcloud import error_reporting
   >>> client = error_reporting.Client()
   >>> try:
   >>>     raise NameError
   >>> except Exception:
   >>>     client.report(message="Something went wrong")


By default, the client will report the error using the service specified in the client's
constructor, or the default service of "python". The service can also be manually specified
in the parameters:

.. doctest::

   >>> try:
   >>>     raise NameError
   >>> except Exception:
   >>>     client.report(message="Something went wrong", service="login_service")
