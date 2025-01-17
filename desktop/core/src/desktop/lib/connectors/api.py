#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging

from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse, render
from desktop.lib.connectors.lib.impala import Impala
from desktop.lib.connectors.lib.hive import Hive
from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


# TODO: automatically load modules from lib module
# TODO: offer to white/black list available connector classes
CONNECTOR_TYPES = [{
    'nice_name': connector.NAME,
    'dialect': connector.TYPE,
    'interface': connector.INTERFACE,
    'settings': connector.PROPERTIES,
    'id': None,
    'category': 'editor',
    'description': ''
    }
  for connector in [
    Impala(), Hive()
  ]
]
CONNECTOR_TYPES += [
  {'nice_name': "Hive Tez", 'dialect': 'hive-tez', 'interface': 'hiveserver2', 'settings': [{'name': 'server_host', 'value': ''}, {'name': 'server_port', 'value': ''},], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Hive LLAP", 'dialect': 'hive-llap', 'interface': 'hiveserver2', 'settings': [{'name': 'server_host', 'value': ''}, {'name': 'server_port', 'value': ''},], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Druid", 'dialect': 'sql-druid', 'interface': 'sqlalchemy', 'settings': [{'name': 'url', 'value': 'druid://druid-host.com:8082/druid/v2/sql/'}], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Kafka SQL", 'dialect': 'kafka-sql', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "SparkSQL", 'dialect': 'spark-sql', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "MySQL", 'dialect': 'sql-mysql', 'interface': 'sqlalchemy', 'settings': [{'name': 'url', 'value': 'mysql://username:password@mysq-host:3306/hue'}], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Presto", 'dialect': 'presto', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Athena", 'dialect': 'athena', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Redshift", 'dialect': 'redshift', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Big Query", 'dialect': 'bigquery', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Oracle", 'dialect': 'oracle', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "SQL Database", 'dialect': 'sql-alchemy', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "SQL Database (JDBC)", 'dialect': 'sql-jdbc', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': 'Deprecated: older way to connect to any database.'},
  # solr
  # hbase
  # kafka

  {'nice_name': "PySpark", 'dialect': 'pyspark', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Spark", 'dialect': 'spark', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Pig", 'dialect': 'pig', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Java", 'dialect': 'java', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},

  {'nice_name': "HDFS", 'dialect': 'hdfs', 'settings': [], 'id': None, 'category': 'browsers', 'description': ''},
  {'nice_name': "YARN", 'dialect': 'yarn', 'settings': [], 'id': None, 'category': 'browsers', 'description': ''},
  {'nice_name': "S3", 'dialect': 's3', 'settings': [], 'id': None, 'category': 'browsers', 'description': ''},
  {'nice_name': "ADLS", 'dialect': 'adls-v1', 'settings': [], 'id': None, 'category': 'browsers', 'description': ''},

  {'nice_name': "Hive Metastore", 'dialect': 'hms', 'settings': [], 'id': None, 'category': 'catalogs', 'description': ''},
  {'nice_name': "Atlas", 'dialect': 'atlas', 'settings': [], 'id': None, 'category': 'catalogs', 'description': ''},
  {'nice_name': "Navigator", 'dialect': 'navigator', 'settings': [], 'id': None, 'category': 'catalogs', 'description': ''},

  {'nice_name': "Optimizer", 'dialect': 'optimizer', 'settings': [], 'id': None, 'category': 'optimizers', 'description': ''},

  {'nice_name': "Oozie", 'dialect': 'oozie', 'settings': [], 'id': None, 'category': 'schedulers', 'description': ''},
  {'nice_name': "Celery", 'dialect': 'celery', 'settings': [], 'id': None, 'category': 'schedulers', 'description': '' },
]

CATEGORIES = [
  {"name": "Editor", 'type': 'editor', 'description': ''},
  {"name": "Browsers", 'type': 'browsers', 'description': ''},
  {"name": "Catalogs", 'type': 'catalogs', 'description': ''},
  {"name": "Optimizers", 'type': 'optimizers', 'description': ''},
  {"name": "Schedulers", 'type': 'schedulers', 'description': ''},
  {"name": "Apps", 'type': 'apps', 'description': ''},
  {"name": "Plugins", 'type': 'plugins', 'description': ''},
]


def _group_category_connectors(connectors):
  return [{
    'category': category['type'],
    'category_name': category['name'],
    'description': category['description'],
    'values': [_connector for _connector in connectors if _connector['category'] == category['type']],
  } for category in CATEGORIES
]

AVAILABLE_CONNECTORS = _group_category_connectors(CONNECTOR_TYPES)


# TODO: persist in DB
# TODO: remove installed connectors that don't have a connector or are blacklisted
# TODO: load back from DB and apply Category properties, e.g. defaults, interface, category, category_name...
# TODO: connector groups: if we want one type (e.g. Hive) to show-up with multiple computes and the same saved query.
# TODO: type --> name, type --> SQL language, e.g. mysql

# connector_type: engine, engine_type: sql, language: hive, hive tez, hiveserver2 + endpoint
CONNECTOR_INSTANCES = [{
    'nice_name': 'Impala', 'name': 'impala-1',
    'dialect': Impala().TYPE, 'interface': Impala().INTERFACE, 'settings': Impala().PROPERTIES, 'is_sql': True, 'id': 1, 'category': 'editor', 'description': ''
  }, {
    'nice_name': 'Hive', 'name': 'hive-1',
    'dialect': Hive().TYPE, 'interface': Hive().INTERFACE, 'settings': Hive().PROPERTIES, 'is_sql': True, 'id': 2, 'category': 'editor', 'description': ''
  }, {
    'nice_name': 'Hive c5', 'name': 'hive-2',
    'dialect': Hive().TYPE, 'interface': Hive().INTERFACE, 'settings': Hive().PROPERTIES, 'is_sql': True, 'id': 3, 'category': 'editor', 'description': ''
  }, {
    'nice_name': 'MySQL', 'name': 'mysql-1',
    'dialect': 'mysql', 'interface': 'sqlalchemy', 'settings': [], 'is_sql': True, 'id': 4, 'category': 'editor', 'description': ''
  },
]

CONNECTOR_INSTANCES[0]['settings'] = [
  {'name': 'server_host', 'value': 'self-service-dw2-2.gce.cloudera.com'},
  {'name': 'server_port', 'value': '21050'},
]
CONNECTOR_INSTANCES[1]['settings'] = [
  {'name': 'server_host', 'value': 'self-service-dw2-1.gce.cloudera.com'},
  {'name': 'server_port', 'value': '10000'},
]
CONNECTOR_INSTANCES[2]['settings'] = [
  {'name': 'server_host', 'value': 'nightly6x-unsecure-1.vpc.cloudera.com'},
  {'name': 'server_port', 'value': '10000'},
]
CONNECTOR_INSTANCES[3]['settings'] = [
  {'name': 'url', 'value': 'mysql://hue:datasshue@romain2:3306/hue'},
]


def get_connector_classes(request):
  global AVAILABLE_CONNECTORS
  global CATEGORIES

  return JsonResponse({
    'connectors': AVAILABLE_CONNECTORS,
    'categories': CATEGORIES
  })


def get_installed_connectors(request):
  return JsonResponse({
    'connectors': _group_category_connectors(CONNECTOR_INSTANCES),
  })


def new_connector(request, dialect):
  instance = _get_connector_by_type(dialect)

  instance['nice_name'] = dialect.title()

  return JsonResponse({'connector': instance})


def get_connector(request, id):
  instance = _get_connector_by_id(id)

  return JsonResponse(instance)

CONNECTOR_IDS = 10

def update_connector(request):
  global CONNECTOR_IDS

  connector = json.loads(request.POST.get('connector'), '{}')
  saved_as = False

  if connector.get('id'):
    instance = _get_connector_by_id(connector['id'])
    instance.update(connector)
  else:
    saved_as = True
    instance = connector
    instance['id'] = CONNECTOR_IDS
    instance['nice_name'] = instance['nice_name']
    instance['name'] = '%s-%s' % (instance['dialect'], CONNECTOR_IDS)
    instance['is_sql'] = instance.get('interface') in ("hiveserver2", "sqlalchemy")
    CONNECTOR_IDS += 1
    CONNECTOR_INSTANCES.append(instance)

  return JsonResponse({'connector': instance, 'saved_as': saved_as})


def _get_connector_by_type(dialect):
  global CONNECTOR_TYPES

  instance = filter(lambda connector: connector['dialect'] == dialect, CONNECTOR_TYPES)

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the type %s found.') % type)


def delete_connector(request):
  global CONNECTOR_INSTANCES

  connector = json.loads(request.POST.get('connector'), '{}')

  size_before = len(CONNECTOR_INSTANCES)
  CONNECTOR_INSTANCES = filter(lambda _connector: _connector['name'] != connector['name'], CONNECTOR_INSTANCES)
  size_after = len(CONNECTOR_INSTANCES)

  if size_before == size_after + 1:
    return JsonResponse({})
  else:
    raise PopupException(_('No connector with the name %(name)s found.') % connector)


def _get_connector_by_id(id):
  global CONNECTOR_INSTANCES

  instance = filter(lambda connector: connector['id'] == id, CONNECTOR_INSTANCES)

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the id %s found.') % id)
