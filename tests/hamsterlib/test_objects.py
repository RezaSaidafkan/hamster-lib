# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str

import pytest
import copy
import datetime
import faker as faker_
from freezegun import freeze_time

from hamsterlib import Category, Activity, Fact

faker = faker_.Faker()


class TestCategory(object):
    def test_init_valid(self, name_string_valid_parametrized, pk_valid_parametrized):
        """Make sure that Category constructor accepts all valid values."""
        category = Category(name_string_valid_parametrized, pk_valid_parametrized)
        assert category.name == name_string_valid_parametrized
        assert category.pk == pk_valid_parametrized

    def test_init_invalid(self, name_string_invalid_parametrized):
        """Make sure that Category constructor rejects all invalid values."""
        with pytest.raises(ValueError):
            Category(name_string_invalid_parametrized)

    def test_as_tuple_include_pk(self, category):
        """Make sure categories tuple representation works as intended and pk is included."""
        assert category.as_tuple() == (category.pk, category.name)

    def test_as_tuple_exclude_pf(self, category):
        """Make sure categories tuple representation works as intended and pk is excluded."""
        assert category.as_tuple(include_pk=False) == (False, category.name)

    def test_equal_fields_true(self, category):
        """Make sure that two categories that differ only in their PK compare equal."""
        other_category = copy.deepcopy(category)
        other_category.pk = 1
        assert category.equal_fields(other_category)

    def test_equal_fields_false(self, category):
        """Make sure that two categories that differ not only in their PK compare unequal."""
        other_category = copy.deepcopy(category)
        other_category.pk = 1
        other_category.name += 'foobar'
        assert category.equal_fields(other_category) is False

    def test__eq__false(self, category):
        """Make sure that two distinct categories return ``False``."""
        other_category = copy.deepcopy(category)
        other_category.pk = 1
        assert category is not other_category
        assert category != other_category

    def test__eq__true(self, category):
        """Make sure that two identical categories return ``True``."""
        other_category = copy.deepcopy(category)
        assert category is not other_category
        assert category == other_category

    def test__str__(self, category):
        """Test string representation."""
        assert '{name}'.format(name=category.name) == str(category)

    def test__repr__(self, category):
        """Test debug representation."""
        assert '[{pk}] {name}'.format(pk=category.pk, name=category.name) == repr(category)


class TestActivity(object):
    def test_init_valid(self, name_string_valid_parametrized, pk_valid_parametrized,
            category_valid_parametrized, deleted_valid_parametrized):
        """Test that init accepts all valid values."""
        activity = Activity(name_string_valid_parametrized, pk=pk_valid_parametrized,
            category=category_valid_parametrized, deleted=deleted_valid_parametrized)
        assert activity.name == name_string_valid_parametrized
        assert activity.pk == pk_valid_parametrized
        assert activity.category == category_valid_parametrized
        assert activity.deleted == bool(deleted_valid_parametrized)

    def test_init_invalid(self, name_string_invalid_parametrized):
        """
        Test that init rejects all invalid values.

        Note:
            Right now, the only aspect that can have concievable invalid value
            is the name.
        """
        with pytest.raises(ValueError):
            Activity(name_string_invalid_parametrized)

    def test_create_from_composite(self, activity):
        result = Activity.create_from_composite(activity.name, activity.category.name)
        assert result.name == activity.name
        assert result.category == activity.category

    def test_as_tuple_include_pk(self, activity):
        """Make sure that conversion to a tuple matches our expectations."""
        assert activity.as_tuple() == (activity.pk, activity.name,
            activity.category, activity.deleted)

    def test_as_tuple_exclude_pk(self, activity):
        """Make sure that conversion to a tuple matches our expectations."""
        assert activity.as_tuple(include_pk=False) == (False, activity.name,
            (False, activity.category.name), activity.deleted)

    def test_equal_fields_true(self, activity):
        """Make sure that two activities that differ only in their PK compare equal."""
        other = copy.deepcopy(activity)
        other.pk = 1
        assert activity.equal_fields(other)

    def test_equal_fields_false(self, activity):
        """Make sure that two activities that differ not only in their PK compare unequal."""
        other = copy.deepcopy(activity)
        other.pk = 1
        other.name += 'foobar'
        assert activity.equal_fields(other) is False

    def test__eq__false(self, activity):
        """Make sure that two distinct activities return ``False``."""
        other = copy.deepcopy(activity)
        other.pk = 1
        assert activity is not other
        assert activity != other

    def test__eq__true(self, activity):
        """Make sure that two identical activities return ``True``."""
        other = copy.deepcopy(activity)
        assert activity is not other
        assert activity == other

    def test__str__without_category(self, activity):
        activity.category = None
        assert str(activity) == '{name}'.format(name=activity.name)

    def test__str__with_category(self, activity):
        assert str(activity) == '{name} ({category})'.format(
            name=activity.name, category=activity.category.name)

    def test__repr__with_category(self, activity):
        """Make sure our debugging representation matches our expectations."""
        assert repr(activity) == '[{pk}] {name} ({category})'.format(
            pk=activity.pk, name=activity.name, category=activity.category.name)

    def test__repr__without_category(self, activity):
        """Make sure our debugging representation matches our expectations."""
        activity.category = None
        assert repr(activity) == '[{pk}] {name}'.format(pk=activity.pk, name=activity.name)


class TestFact(object):
    def test_fact_init_valid(self, activity, start_end_datetimes, pk_valid_parametrized,
            description_valid_parametrized, tag_list_valid_parametrized):
        """Make sure valid values instaniate a Fact."""

        fact = Fact(activity, start_end_datetimes[0], start_end_datetimes[1],
            pk_valid_parametrized, description_valid_parametrized, tag_list_valid_parametrized)
        assert fact.activity == activity
        assert fact.pk == pk_valid_parametrized
        assert fact.description == description_valid_parametrized
        assert fact.start == start_end_datetimes[0]
        assert fact.end == start_end_datetimes[1]
        assert fact.tags == tag_list_valid_parametrized

    def test_create_from_raw_fact_valid(self, raw_fact_parametrized):
        """Make sure the constructed ``Fact``s anatomy reflets our expectations."""
        raw_fact, expectation = raw_fact_parametrized
        fact = Fact.create_from_raw_fact(raw_fact)
        assert fact.start == expectation['start']
        assert fact.end == expectation['end']
        assert fact.activity.name == expectation['activity']
        if fact.activity.category:
            assert fact.activity.category.name == expectation['category']
        else:
            assert expectation['category'] is None
        assert fact.description == expectation['description']

    def test_create_from_raw_fact_invalid(self, invalid_raw_fact_parametrized):
        """Make sure invalid string raises an exception."""
        with pytest.raises(ValueError):
            Fact.create_from_raw_fact(invalid_raw_fact_parametrized)

    @pytest.mark.parametrize(('raw_fact', 'expectations'), [
        ('-7 foo@bar, palimpalum',
         {'start': datetime.datetime(2015, 5, 2, 18, 0, 0),
          'end': None,
          'activity': 'foo',
          'category': 'bar',
          'description': 'palimpalum'},
         ),
    ])
    @freeze_time('2015-05-02 18:07')
    def test_create_from_raw_fact_with_delta(self, raw_fact, expectations):
        fact = Fact.create_from_raw_fact(raw_fact)
        assert fact.start == expectations['start']

    @pytest.mark.parametrize('start', [None, faker.date_time()])
    def test_start_valid(self, fact, start):
        """Make sure that valid arguments get stored by the setter."""
        fact.start = start
        assert fact.start == start

    def test_start_invalid(self, fact):
        """Make sure that trying to store dateimes as strings throws an error."""
        with pytest.raises(TypeError):
            fact.start = faker.date_time().strftime('%y-%m-%d %H:%M')

    @pytest.mark.parametrize('end', [None, faker.date_time()])
    def test_end_valid(self, fact, end):
        """Make sure that valid arguments get stored by the setter."""
        fact.end = end
        assert fact.end == end

    def test_end_invalid(self, fact):
        """Make sure that trying to store dateimes as strings throws an error."""
        with pytest.raises(TypeError):
            fact.end = faker.date_time().strftime('%y-%m-%d %H:%M')

    def test_description_valid(self, fact, description_valid_parametrized):
        """Make sure that valid arguments get stored by the setter."""
        fact.description = description_valid_parametrized
        assert fact.description == description_valid_parametrized

    def test_delta(self, fact):
        """Make sure that valid arguments get stored by the setter."""
        assert fact.delta == fact.end - fact.start

    def test_delta_no_end(self, fact):
        """Make sure that a missing end datetime results in ``delta=None``."""
        fact.end = None
        assert fact.delta is None

    @pytest.mark.parametrize('offset', [
        (15, {'%M': '15', '%H:%M': '00:15'}),
        (452, {'%M': '452', '%H:%M': '07:32'}),
        (912, {'%M': '912', '%H:%M': '15:12'}),
    ])
    def test_get_string_delta_valid_format(self, fact, offset,
            start_end_datetimes_from_offset, string_delta_format_parametrized):
        """Make sure that the resulting string matches our expectation."""
        offset, expectation = offset
        fact.start, fact.end = start_end_datetimes_from_offset(offset)
        result = fact.get_string_delta(string_delta_format_parametrized)
        assert result == expectation[string_delta_format_parametrized]

    def test_get_string_delta_invalid_format(self, fact):
        """Ensure that passing an invalid format will raise an exception."""
        with pytest.raises(ValueError):
            fact.get_string_delta('foobar')

    def test_date(self, fact):
        """Make sure the property returns just the date of ``Fact().start``."""
        assert fact.date == fact.start.date()

    def test_serialized_name_with_category_and_description(self, fact):
        """Make sure that the property returns a string matching our expectation."""
        expectation = '{f.activity.name}@{f.category.name}, {f.description}'.format(f=fact)
        assert fact.serialized_name == expectation

    def test_serialized_name_with_category_no_description(self, fact):
        """Make sure that the property returns a string matching our expectation."""
        fact.description = None
        expectation = '{f.activity.name}@{f.category.name}'.format(f=fact)
        assert fact.serialized_name == expectation

    def test_serialized_name_with_description_no_category(self, fact):
        """Make sure that the property returns a string matching our expectation."""
        fact.activity.category = None
        expectation = '{f.activity.name}, {f.description}'.format(f=fact)
        assert fact.serialized_name == expectation

    def test_category_property(self, fact):
        """Make sure the property returns this facts category."""
        assert fact.category == fact.activity.category

    def test_as_tuple_include_pk(self, fact):
        """Make sure that conversion to a tuple matches our expectations."""
        assert fact.as_tuple() == (fact.pk, fact.activity.as_tuple(include_pk=True),
            fact.start, fact.end, fact.description, fact.tags)

    def test_as_tuple_exclude_pk(self, fact):
        """Make sure that conversion to a tuple matches our expectations."""
        assert fact.as_tuple(include_pk=False) == (False, fact.activity.as_tuple(include_pk=False),
            fact.start, fact.end, fact.description, fact.tags)

    def test_equal_fields_true(self, fact):
        """Make sure that two facts that differ only in their PK compare equal."""
        other = copy.deepcopy(fact)
        other.pk = 1
        assert fact.equal_fields(other)

    def test_equal_fields_false(self, fact):
        """Make sure that two facts that differ not only in their PK compare unequal."""
        other = copy.deepcopy(fact)
        other.pk = 1
        other.description += 'foobar'
        assert fact.equal_fields(other) is False

    def test__eq__false(self, fact):
        """Make sure that two distinct facts return ``False``."""
        other = copy.deepcopy(fact)
        other.pk = 1
        assert fact is not other
        assert fact != other

    def test__eq__true(self, fact):
        """Make sure that two identical facts return ``True``."""
        other = copy.deepcopy(fact)
        assert fact is not other
        assert fact == other

    def test__str__(self, fact):
        expectation = '{start} - {end} {serialized_name}'.format(
            start=fact.start.strftime("%d-%m-%Y %H:%M"),
            end=fact.end.strftime("%H:%M"),
            serialized_name=fact.serialized_name)
        assert str(fact) == expectation

    def test__str__no_end(self, fact):
        fact.end = None
        expectation = '{start} {serialized_name}'.format(
            start=fact.start.strftime("%d-%m-%Y %H:%M"),
            serialized_name=fact.serialized_name)
        assert str(fact) == expectation

    def test__repr__(self, fact):
        expectation = '{start} - {end} {serialized_name}'.format(
            start=fact.start.strftime("%d-%m-%Y %H:%M"),
            end=fact.end.strftime("%H:%M"),
            serialized_name=fact.serialized_name)
        assert repr(fact) == expectation

    def test__repr__no_end(self, fact):
        fact.end = None
        expectation = '{start} {serialized_name}'.format(
            start=fact.start.strftime("%d-%m-%Y %H:%M"),
            serialized_name=fact.serialized_name)
        assert repr(fact) == expectation