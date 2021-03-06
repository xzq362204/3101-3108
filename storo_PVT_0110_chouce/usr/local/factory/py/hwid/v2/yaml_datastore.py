# pylint: disable=E1101
# Copyright 2011 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import difflib
import logging
import os
import yaml


# Warning message prepended to all datastore files.
DATA_FILE_WARNING_MESSAGE_HEADER = '''
# WARNING: This file is AUTOMATICALLY GENERATED, do not edit.
# The proper way to modify this file is using the hwid_tool.
'''.strip()


def YamlWrite(structured_data, dumper):
  """Wrap yaml.dump to make calling convention consistent."""
  return yaml.dump(structured_data, default_flow_style=False, Dumper=dumper)


def YamlRead(serialized_data, loader):
  """Wrap yaml.load to make calling convention consistent."""
  return yaml.load(serialized_data, Loader=loader)


class InvalidDataError(ValueError):
  """Error in (en/de)coding or validating data."""
  pass


class YamlDatastore:

  def WriteOnDiff(self, path, filename, raw_data):
    """Write data to file if there are any differences, logging the diffs.

    The file will be created if it does not exist.
    """
    full_path = os.path.join(path, filename)
    internal_data = (DATA_FILE_WARNING_MESSAGE_HEADER.split('\n') +
                     raw_data.strip('\n').split('\n'))
    if os.path.exists(full_path):
      file_data = [line.rstrip('\n') for line in open(full_path, 'r')]
      diff = [line for line in difflib.unified_diff(file_data, internal_data)]
      if not diff:
        logging.debug('no differences for %s', full_path)
        return
      logging.info('updating %s with changes:\n%s', filename, '\n'.join(diff))
    else:
      logging.info('creating new data file %s', filename)
    with open(full_path, 'w') as f:
      f.write('%s\n' % '\n'.join(internal_data))


class _DatastoreBase:

  def __init__(self, **field_dict):
    """Creates object using the field data specified in field_dict."""
    self.__dict__.update(field_dict)

  def Yrepr(self, yaml_representer):
    """The object YAML representation is just its field_dict data."""
    return yaml_representer.represent_data(self.__dict__)

  def Encode(self, dumper=yaml.Dumper, loader=yaml.SafeLoader):
    """Return the YAML string for this object and check its schema.

    After generating the output data, run decode on that to validate.
    """
    yaml_data = YamlWrite(self, dumper)
    self.Decode(yaml_data, loader)
    return yaml_data

  @classmethod
  def New(cls):
    field_dict = {}
    for elt_key, elt_type in cls._schema.items():
      if isinstance(elt_type, tuple):
        elt_data = {} if elt_type[0] is dict else []
      elif issubclass(elt_type, _DatastoreBase):
        elt_data = elt_type.New()
      else:
        elt_data = ''
      field_dict[elt_key] = elt_data
    return cls(**field_dict)

  @classmethod
  def Decode(cls, data, loader=yaml.SafeLoader):
    """Given YAML string, creates corresponding object and check its schema."""
    def NestedDecode(elt_type, elt_data):
      """Apply appropriate constructors to nested object data."""
      if isinstance(elt_type, tuple):
        collection_type, field_type = elt_type
        if collection_type is dict:
          return {field_key: NestedDecode(field_type, field)
                  for field_key, field in elt_data.items()}
        if collection_type is list:
          return sorted(NestedDecode(field_type, field) for field in elt_data)
      elif isinstance(elt_type, list):
        for elt_subtype in elt_type:
          try:
            return NestedDecode(elt_subtype, elt_data)
          except Exception:
            continue
      elif issubclass(elt_type, _DatastoreBase):
        cooked_field_dict = dict(
            (subelt_key, NestedDecode(subelt_type, elt_data[subelt_key]))
            # pylint: disable=W0212
            for subelt_key, subelt_type in elt_type._schema.items())
        return elt_type(**cooked_field_dict)
      elif isinstance(elt_data, elt_type):
        return elt_data
      raise InvalidDataError
    try:
      field_dict = YamlRead(data, loader)
    except yaml.YAMLError as e:
      raise InvalidDataError('YAML deserialization error: %s' % e)
    cls.ValidateSchema(field_dict)
    cooked_field_dict = dict(
        (elt_key, NestedDecode(elt_type, field_dict[elt_key]))
        for elt_key, elt_type in cls._schema.items())
    return cls(**cooked_field_dict)

  @classmethod
  def FieldNames(cls):
    return list(cls._schema)

  @classmethod
  def ValidateSchema(cls, field_dict):
    """Ensures the layout of field_dict matches the class schema specification.

    This should be run before data is coerced into objects.  When the
    schema indicates an object class type, the corresponding schema
    for that class is applied to the corresponding subset of field
    data.  Long story short, field_dict should not contain any
    objects.

    Args:
      field_dict: Data which must have layout and type matching schema.
    """
    def ValidateCollection(top_level_tag, collection_type_data,
                           collection_data):
      if len(collection_type_data) != 2:
        raise InvalidDataError(
            '%r schema contains bad type definiton for element %r, ' %
            (cls.__name__, top_level_tag) +
            'expected (collection type, field type) tuple, '
            'found %s' % repr(collection_type_data))
      collection_type, field_type = collection_type_data
      if collection_type not in [dict, list]:
        raise InvalidDataError(
            '%r schema element %r has illegal collection type %r ' %
            (cls.__name__, top_level_tag, collection_type.__name__) +
            '(only "dict" and "list" are supported)')
      if not isinstance(collection_data, collection_type):
        raise InvalidDataError(
            '%r schema validation failed for element %r, ' %
            (cls.__name__, top_level_tag) +
            'expected type %r, found %r' %
            (collection_type.__name__, type(collection_data).__name__))
      if collection_type is dict:
        for field_key, field_data in collection_data.items():
          if not (isinstance(field_key, str) or isinstance(field_key, int)):
            raise InvalidDataError(
                '%r schema validation failed for element %r, ' %
                (cls.__name__, top_level_tag) +
                'dict key must be "str" or "int", found %r' %
                (type(field_key).__name__))
          ValidateField(top_level_tag, field_type, field_data)
      elif collection_type is list:
        for field_data in collection_data:
          ValidateField(top_level_tag, field_type, field_data)

    def ValidateField(top_level_tag, field_type, field_data):
      if isinstance(field_type, tuple):
        ValidateCollection(top_level_tag, field_type, field_data)
        return
      if isinstance(field_type, list):
        for field_subtype in field_type:
          try:
            ValidateField(top_level_tag, field_subtype, field_data)
            return
          except InvalidDataError:
            continue
      elif issubclass(field_type, _DatastoreBase):
        field_type.ValidateSchema(field_data)
        return
      elif isinstance(field_data, field_type):
        return
      raise InvalidDataError(
          '%r schema validation failed for element %r, expected type %r,'
          ' found %r' % (cls.__name__, top_level_tag, field_type,
                         type(field_data).__name__))
    if set(cls._schema) ^ set(field_dict):
      raise InvalidDataError(
          '%r schema and data dict keys do not match, ' % cls.__name__ +
          'data is missing keys: %r, ' %
          sorted(set(cls._schema) - set(field_dict)) +
          'data has extra keys: %r' %
          sorted(set(field_dict) - set(cls._schema)))
    for top_level_tag, field_type in cls._schema.items():
      ValidateField(top_level_tag, field_type, field_dict[top_level_tag])


def MakeDatastoreClass(class_name, class_schema):
  """Define storable object type with a schema and yaml representer.

  The yaml representer is added so that yaml calls the appropriate Yrepr
  function for the object, instead of the generic tagged python object format.

  Args:
    class_name: Name of the class to be defined.
    class_schema: A dict describing the class schema, which will
      be enforced whenever the class data is written to the backing
      store.  The dict must contain a key for each data field, and the
      corresponding value is the type of that field ; value types can
      be singleton python types, or they can be 2-tuples.  For tuples,
      the lhs must be either dict or list, and the rhs can be either a
      singleton or recursively another tuple.  The keys for dicts are
      implicitly enforced to always be of type str.  There must be a
      field called 'name', which is used as an index by the backing
      store.
  Returns:
    The new created class.
  """
  cls = type(class_name, (_DatastoreBase,), {})
  cls._schema = class_schema  # pylint: disable=W0212
  yaml.add_representer(cls, lambda yaml_repr, obj: obj.Yrepr(yaml_repr))
  return cls
