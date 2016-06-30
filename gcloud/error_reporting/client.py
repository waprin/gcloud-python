#!/usr/bin/env python
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Client for interacting with the Stackdriver Logging API"""

import traceback

import gcloud.logging.client


class Client(object):
    """Error Reporting client. Currently Error Reporting is done by creating
    a Logging client.

    :type project: string
    :param project: the project which the client acts on behalf of. If not
                    passed falls back to the default inferred from the
                    environment.

    :type credentials: :class:`oauth2client.client.OAuth2Credentials` or
                       :class:`NoneType`
    :param credentials: The OAuth2 Credentials to use for the connection
                        owned by this client. If not passed (and if no ``http``
                        object is passed), falls back to the default inferred
                        from the environment.

    :type http: :class:`httplib2.Http` or class that defines ``request()``.
    :param http: An optional HTTP object to make requests. If not passed, an
                 ``http`` object is created that is bound to the
                 ``credentials`` for the current object.

    :type service: str
    :param service: An identifier of the service, such as the name of the
                    executable, job, or Google App Engine service name. This
                    field is expected to have a low number of values that are
                    relatively stable over time, as opposed to version,
                    which can be changed whenever new code is deployed.


    :type version: str
    :param version: Represents the source code version that the developer
                    provided, which could represent a version label or a Git
                    SHA-1 hash, for example. If the developer did not provide
                    a version, the value is set to default.

    :raises: :class:`ValueError` if the project is neither passed in nor
             set in the environment.
    """

    def __init__(self, project=None,
                 credentials=None,
                 http=None,
                 service=None,
                 version=None):
        self.logging_client = gcloud.logging.client.Client(
            project, credentials, http)
        self.service = service
        self.version = version

    DEFAULT_SERVICE = 'python'

    def _get_default_service(self):
        """Returns the service to use on method calls that don't specify an
        override.

          :rtype: string
          :returns: The default service for error reporting calls
        """
        if self.service:
            return self.service
        else:
            return self.DEFAULT_SERVICE

    def _get_default_version(self):
        """Returns the service to use on method calls that don't specify an
        override.

        :rtype: string
        :returns: The default version for error reporting calls.
        """
        if self.version:
            return self.version

    def report(self, message="", service=None, version=None):
        """ Reports the details of the latest exceptions to Stackdriver Error
            Reporting.

         https://cloud.google.com/error-reporting/docs/formatting-error-messages

           :type message: str
           :param message: An optional message to include with the exception
                           detail

           :type service: str
           :param service: An identifier of the service, such as the name of
                           the executable, job, or Google App Engine service
                           name. This field is expected to have a low number
                           of values that are relatively stable over time,
                           as opposed to version, which can be changed
                           whenever new code is deployed.

           :type version: str
           :param version: Represents the source code version that the
                           developer provided, which could represent a
                           version label or a Git SHA-1 hash, for example. If
                           the developer did not provide a version, the value
                           is set to default.


           Example::

                >>>     try:
                >>>         raise NameError
                >>>     except Exception:
                >>>         client.report("Something went wrong!")
        """
        if not service:
            service = self._get_default_service()
        if not version:
            version = self._get_default_version()
        payload = {
            'serviceContext': {
                'service': service,
            },
            'message': '{0} : {1}'.format(message, traceback.format_exc())
        }
        if version:
            payload['serviceContext']['version'] = version
        logger = self.logging_client.logger('errors')
        logger.log_struct(payload)
