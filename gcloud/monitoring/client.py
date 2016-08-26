# Copyright 2016 Google Inc. All rights reserved.
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

"""Client for interacting with the `Google Stackdriver Monitoring API (V3)`_.

Example::

    >>> from gcloud import monitoring
    >>> client = monitoring.Client()
    >>> query = client.query(minutes=5)
    >>> print(query.as_dataframe())  # Requires pandas.

At present, the client supports querying of time series, metric descriptors,
and monitored resource descriptors.

.. _Google Stackdriver Monitoring API (V3):
    https://cloud.google.com/monitoring/api/v3/
"""

import datetime

from gcloud.client import JSONClient
from gcloud.monitoring.connection import Connection
from gcloud.monitoring.group import Group
from gcloud.monitoring.metric import Metric
from gcloud.monitoring.metric import MetricDescriptor
from gcloud.monitoring.metric import MetricKind
from gcloud.monitoring.metric import ValueType
from gcloud.monitoring.query import Query
from gcloud.monitoring.resource import Resource
from gcloud.monitoring.resource import ResourceDescriptor
from gcloud.monitoring.timeseries import Point
from gcloud.monitoring.timeseries import TimeSeries

_UTCNOW = datetime.datetime.utcnow  # To be replaced by tests.


class Client(JSONClient):
    """Client to bundle configuration needed for API requests.

    :type project: string
    :param project: The target project. If not passed, falls back to the
                    default inferred from the environment.

    :type credentials: :class:`oauth2client.client.OAuth2Credentials` or
                       :class:`NoneType`
    :param credentials: The OAuth2 Credentials to use for the connection
                        owned by this client. If not passed (and if no ``http``
                        object is passed), falls back to the default inferred
                        from the environment.

    :type http: :class:`httplib2.Http` or class that defines ``request()``
    :param http: An optional HTTP object to make requests. If not passed, an
                 ``http`` object is created that is bound to the
                 ``credentials`` for the current object.
    """

    _connection_class = Connection

    def query(self,
              metric_type=Query.DEFAULT_METRIC_TYPE,
              end_time=None,
              days=0, hours=0, minutes=0):
        """Construct a query object for retrieving metric data.

        Example::

            >>> query = client.query(minutes=5)
            >>> print(query.as_dataframe())  # Requires pandas.

        :type metric_type: string
        :param metric_type: The metric type name. The default value is
            :data:`Query.DEFAULT_METRIC_TYPE
            <gcloud.monitoring.query.Query.DEFAULT_METRIC_TYPE>`,
            but please note that this default value is provided only for
            demonstration purposes and is subject to change. See the
            `supported metrics`_.

        :type end_time: :class:`datetime.datetime` or None
        :param end_time: The end time (inclusive) of the time interval
            for which results should be returned, as a datetime object.
            The default is the start of the current minute.

            The start time (exclusive) is determined by combining the
            values of  ``days``, ``hours``, and ``minutes``, and
            subtracting the resulting duration from the end time.

            It is also allowed to omit the end time and duration here,
            in which case
            :meth:`~gcloud.monitoring.query.Query.select_interval`
            must be called before the query is executed.

        :type days: integer
        :param days: The number of days in the time interval.

        :type hours: integer
        :param hours: The number of hours in the time interval.

        :type minutes: integer
        :param minutes: The number of minutes in the time interval.

        :rtype: :class:`~gcloud.monitoring.query.Query`
        :returns: The query object.

        :raises: :exc:`ValueError` if ``end_time`` is specified but
            ``days``, ``hours``, and ``minutes`` are all zero.
            If you really want to specify a point in time, use
            :meth:`~gcloud.monitoring.query.Query.select_interval`.

        .. _supported metrics: https://cloud.google.com/monitoring/api/metrics
        """
        return Query(self, metric_type,
                     end_time=end_time,
                     days=days, hours=hours, minutes=minutes)

    def metric_descriptor(self, type_,
                          metric_kind=MetricKind.METRIC_KIND_UNSPECIFIED,
                          value_type=ValueType.VALUE_TYPE_UNSPECIFIED,
                          labels=(), unit='', description='', display_name=''):
        """Construct a metric descriptor object.

        Metric descriptors specify the schema for a particular metric type.

        This factory method is used most often in conjunction with the metric
        descriptor :meth:`~gcloud.monitoring.metric.MetricDescriptor.create`
        method to define custom metrics::

            >>> descriptor = client.metric_descriptor(
            ...     'custom.googleapis.com/my_metric',
            ...     metric_kind=MetricKind.GAUGE,
            ...     value_type=ValueType.DOUBLE,
            ...     description='This is a simple example of a custom metric.')
            >>> descriptor.create()

        Here is an example where the custom metric is parameterized by a
        metric label::

            >>> label = LabelDescriptor('response_code', LabelValueType.INT64,
            ...                         description='HTTP status code')
            >>> descriptor = client.metric_descriptor(
            ...     'custom.googleapis.com/my_app/response_count',
            ...     metric_kind=MetricKind.CUMULATIVE,
            ...     value_type=ValueType.INT64,
            ...     labels=[label],
            ...     description='Cumulative count of HTTP responses.')
            >>> descriptor.create()

        :type type_: string
        :param type_:
            The metric type including a DNS name prefix. For example:
            ``"custom.googleapis.com/my_metric"``

        :type metric_kind: string
        :param metric_kind:
            The kind of measurement. It must be one of
            :data:`MetricKind.GAUGE`, :data:`MetricKind.DELTA`,
            or :data:`MetricKind.CUMULATIVE`.
            See :class:`~gcloud.monitoring.metric.MetricKind`.

        :type value_type: string
        :param value_type:
            The value type of the metric. It must be one of
            :data:`ValueType.BOOL`, :data:`ValueType.INT64`,
            :data:`ValueType.DOUBLE`, :data:`ValueType.STRING`,
            or :data:`ValueType.DISTRIBUTION`.
            See :class:`ValueType`.

        :type labels: list of :class:`~gcloud.monitoring.label.LabelDescriptor`
        :param labels:
            A sequence of zero or more label descriptors specifying the labels
            used to identify a specific instance of this metric.

        :type unit: string
        :param unit: An optional unit in which the metric value is reported.

        :type description: string
        :param description: An optional detailed description of the metric.

        :type display_name: string
        :param display_name: An optional concise name for the metric.

        :rtype: :class:`MetricDescriptor`
        :returns: The metric descriptor created with the passed-in arguments.
        """
        return MetricDescriptor(
            self, type_,
            metric_kind=metric_kind,
            value_type=value_type,
            labels=labels,
            unit=unit,
            description=description,
            display_name=display_name,
        )

    @staticmethod
    def metric(type_, labels):
        """Factory for constructing metric objects.

        :class:`~gcloud.monitoring.metric.Metric` objects are typically
        created to write custom metric values. The type should match the
        metric type specified in the
        :class:`~gcloud.monitoring.metric.MetricDescriptor` used to
        create the custom metric::

             >>> metric = client.metric('custom.googleapis.com/my_metric',
             ...                        labels={
             ...                            'status': 'successful',
             ...                         })

        :type type_: string
        :param type_: The metric type name.

        :type labels: dict
        :param labels: A mapping from label names to values for all labels
                       enumerated in the associated
                       :class:`~gcloud.monitoring.metric.MetricDescriptor`.

        :rtype: :class:`~gcloud.monitoring.metric.Metric`
        :returns: The metric object.
        """
        return Metric(type=type_, labels=labels)

    @staticmethod
    def resource(type_, labels):
        """Factory for constructing monitored resource objects.

        A monitored resource object (
        :class:`~gcloud.monitoring.resource.Resource`) is
        typically used to create a
        :class:`~gcloud.monitoring.timeseries.TimeSeries` object.

        For a list of possible monitored resource types and their associated
        labels, see:

        https://cloud.google.com/monitoring/api/resources

        :type type_: string
        :param type_: The monitored resource type name.

        :type labels: dict
        :param labels: A mapping from label names to values for all labels
                       enumerated in the associated
                       :class:`~gcloud.monitoring.resource.ResourceDescriptor`,
                       except that ``project_id`` can and should be omitted
                       when writing time series data.

        :rtype: :class:`~gcloud.monitoring.resource.Resource`
        :returns: A monitored resource object.
        """
        return Resource(type_, labels)

    @staticmethod
    def time_series(metric, resource, value,
                    end_time=None, start_time=None):
        """Construct a time series object for a single data point.

        .. note::

           While :class:`~gcloud.monitoring.timeseries.TimeSeries` objects
           returned by the API typically have multiple data points,
           :class:`~gcloud.monitoring.timeseries.TimeSeries` objects
           sent to the API must have at most one point.

        For example::

            >>> timeseries = client.time_series(metric, resource, 1.23,
            ...                                 end_time=end)

        For more information, see:

        https://cloud.google.com/monitoring/api/ref_v3/rest/v3/TimeSeries

        :type metric: :class:`~gcloud.monitoring.metric.Metric`
        :param metric: A :class:`~gcloud.monitoring.metric.Metric` object.

        :type resource: :class:`~gcloud.monitoring.resource.Resource`
        :param resource: A :class:`~gcloud.monitoring.resource.Resource`
                         object.

        :type value: bool, int, string, or float
        :param value:
            The value of the data point to create for the
            :class:`~gcloud.monitoring.timeseries.TimeSeries`.

            .. note::

               The Python type of the value will determine the
               :class:`~ValueType` sent to the API, which must match the value
               type specified in the metric descriptor. For example, a Python
               float will be sent to the API as a :data:`ValueType.DOUBLE`.

        :type end_time: :class:`~datetime.datetime`
        :param end_time:
            The end time for the point to be included in the time series.
            Assumed to be UTC if no time zone information is present.
            Defaults to the current time, as obtained by calling
            :meth:`datetime.datetime.utcnow`.

        :type start_time: :class:`~datetime.datetime`
        :param start_time:
            The start time for the point to be included in the time series.
            Assumed to be UTC if no time zone information is present.
            Defaults to None. If the start time is unspecified,
            the API interprets the start time to be the same as the end time.

        :rtype: :class:`~gcloud.monitoring.timeseries.TimeSeries`
        :returns: A time series object.
        """
        if end_time is None:
            end_time = _UTCNOW()
        point = Point(value=value, start_time=start_time, end_time=end_time)
        return TimeSeries(metric=metric, resource=resource, metric_kind=None,
                          value_type=None, points=[point])

    def fetch_metric_descriptor(self, metric_type):
        """Look up a metric descriptor by type.

        Example::

            >>> METRIC = 'compute.googleapis.com/instance/cpu/utilization'
            >>> print(client.fetch_metric_descriptor(METRIC))

        :type metric_type: string
        :param metric_type: The metric type name.

        :rtype: :class:`~gcloud.monitoring.metric.MetricDescriptor`
        :returns: The metric descriptor instance.

        :raises: :class:`gcloud.exceptions.NotFound` if the metric descriptor
            is not found.
        """
        return MetricDescriptor._fetch(self, metric_type)

    def list_metric_descriptors(self, filter_string=None, type_prefix=None):
        """List all metric descriptors for the project.

        Examples::

            >>> for descriptor in client.list_metric_descriptors():
            ...     print(descriptor.type)

            >>> for descriptor in client.list_metric_descriptors(
            ...         type_prefix='custom.'):
            ...     print(descriptor.type)

        :type filter_string: string or None
        :param filter_string:
            An optional filter expression describing the metric descriptors
            to be returned. See the `filter documentation`_.

        :type type_prefix: string or None
        :param type_prefix: An optional prefix constraining the selected
            metric types. This adds ``metric.type = starts_with("<prefix>")``
            to the filter.

        :rtype: list of :class:`~gcloud.monitoring.metric.MetricDescriptor`
        :returns: A list of metric descriptor instances.

        .. _filter documentation:
            https://cloud.google.com/monitoring/api/v3/filters
        """
        return MetricDescriptor._list(self, filter_string,
                                      type_prefix=type_prefix)

    def fetch_resource_descriptor(self, resource_type):
        """Look up a monitored resource descriptor by type.

        Example::

            >>> print(client.fetch_resource_descriptor('gce_instance'))

        :type resource_type: string
        :param resource_type: The resource type name.

        :rtype: :class:`~gcloud.monitoring.resource.ResourceDescriptor`
        :returns: The resource descriptor instance.

        :raises: :class:`gcloud.exceptions.NotFound` if the resource descriptor
            is not found.
        """
        return ResourceDescriptor._fetch(self, resource_type)

    def list_resource_descriptors(self, filter_string=None):
        """List all monitored resource descriptors for the project.

        Example::

            >>> for descriptor in client.list_resource_descriptors():
            ...     print(descriptor.type)

        :type filter_string: string or None
        :param filter_string:
            An optional filter expression describing the resource descriptors
            to be returned. See the `filter documentation`_.

        :rtype: list of :class:`~gcloud.monitoring.resource.ResourceDescriptor`
        :returns: A list of resource descriptor instances.

        .. _filter documentation:
            https://cloud.google.com/monitoring/api/v3/filters
        """
        return ResourceDescriptor._list(self, filter_string)

    def group(self, group_id=None, display_name=None, parent_id=None,
              filter_string=None, is_cluster=False):
        """Factory constructor for group object.

        .. note::
          This will not make an HTTP request; it simply instantiates
          a group object owned by this client.

        :type group_id: string or None
        :param group_id: The ID of the group.

        :type display_name: string or None
        :param display_name:
            A user-assigned name for this group, used only for display
            purposes.

        :type parent_id: string or None
        :param parent_id:
            The ID of the group's parent, if it has one.

        :type filter_string: string or None
        :param filter_string:
            The filter string used to determine which monitored resources
            belong to this group.

        :type is_cluster: boolean
        :param is_cluster:
            If true, the members of this group are considered to be a cluster.
            The system can perform additional analysis on groups that are
            clusters.

        :rtype: :class:`Group`
        :returns: The group created with the passed-in arguments.

        :raises:
            :exc:`ValueError` if both ``group_id`` and ``name`` are specified.
        """
        return Group(
            self,
            group_id=group_id,
            display_name=display_name,
            parent_id=parent_id,
            filter_string=filter_string,
            is_cluster=is_cluster,
        )

    def fetch_group(self, group_id):
        """Fetch a group from the API based on it's ID.

        Example::

            >>> try:
            >>>     group = client.fetch_group('1234')
            >>> except gcloud.exceptions.NotFound:
            >>>     print('That group does not exist!')

        :type group_id: string
        :param group_id: The ID of the group.

        :rtype: :class:`~gcloud.monitoring.group.Group`
        :returns: The group instance.

        :raises: :class:`gcloud.exceptions.NotFound` if the group is not found.
        """
        return Group._fetch(self, group_id)

    def list_groups(self):
        """List all groups for the project.

        Example::

            >>> for group in client.list_groups():
            ...     print((group.display_name, group.name))

        :rtype: list of :class:`~gcloud.monitoring.group.Group`
        :returns: A list of group instances.
        """
        return Group._list(self)

    def write_time_series(self, timeseries_sequence):
        """Writes a sequence of time series to the API.

        The recommended approach to creating time series objects is using
        the :meth:`gcloud.monitoring.client.Client.time_series` factory.

        For writing a single time series, consider using the
        :meth:`~gcloud.monitoring.client.Client.write_point` method.

        Example::

            >>> client.write_time_series([ts1, ts2])

        :type timeseries_sequence:
            sequence of :class:`gcloud.monitoring.timeseries.TimeSeries`.
        :param timeseries_sequence:
            A sequence (typically a tuple or list) of time series to be written
            to the API. Each time series must contain exactly one point.
        """
        path = '/projects/{project}/timeSeries/'.format(
            project=self.project)
        timeseries_dict = [t._to_dict() for t in timeseries_sequence]
        self.connection.api_request(method='POST', path=path,
                                    data={'timeSeries': timeseries_dict})

    def write_point(self, metric, resource, value,
                    end_time=None,
                    start_time=None):
        """Writes a single point for a metric to the API.

        This is a convenience method to write a single time series objects to
        the API. To write multiple time series to the API as a batch, consider
        using the :meth:`gcloud.monitoring.client.Client.time_series` factory
        to create time series and the
        :meth:`gcloud.monitoring.client.Client.time_series` method to write
        the objects.

        Example::

            >>> client.write_point(metric, resource, 3.14)

        :type metric: :class:`~gcloud.monitoring.metric.Metric`
        :param metric: A :class:`~gcloud.monitoring.metric.Metric` object.

        :type resource: :class:`~gcloud.monitoring.resource.Resource`
        :param resource: A :class:`~gcloud.monitoring.resource.Resource`
                         object.

        :type value: bool, int, string, or float
        :param value:
            The value of the data point to create for the
            :class:`~gcloud.monitoring.timeseries.TimeSeries`.

            .. note::

               The Python type of the value will determine the
               :class:`~ValueType` sent to the API, which must match the value
               type specified in the metric descriptor. For example, a Python
               float will be sent to the API as a :data:`ValueType.DOUBLE`.

        :type end_time: :class:`~datetime.datetime`
        :param end_time:
            The end time for the point to be included in the time series.
            Assumed to be UTC if no time zone information is present.
            Defaults to the current time, as obtained by calling
            :meth:`datetime.datetime.utcnow`.

        :type start_time: :class:`~datetime.datetime`
        :param start_time:
            The start time for the point to be included in the time series.
            Assumed to be UTC if no time zone information is present.
            Defaults to None. If the start time is unspecified,
            the API interprets the start time to be the same as the end time.
        """
        timeseries = self.time_series(
            metric, resource, value, end_time, start_time)
        self.write_time_series([timeseries])
