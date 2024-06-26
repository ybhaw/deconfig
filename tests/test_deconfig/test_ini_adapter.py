"""
Unit tests for the `deconfig.ini_adapter` module.
"""

from configparser import NoOptionError
from unittest.mock import patch

import pytest

from deconfig import IniAdapter, field
from deconfig.core import AdapterBase, AdapterError


@pytest.fixture(name="field_decorated_callable")
def fixture_field_decorated_callable():
    @field(name="stub_field")
    def stub_callable():
        """Field decorated stub callable"""

    return stub_callable


@pytest.fixture(name="configparser")
def fixture_configparser():
    with patch(
        f"{IniAdapter.__module__}.configparser.ConfigParser", autospec=True
    ) as parser:
        yield parser


def _flatten_array(array_of_array):
    res = []
    arrays = list(filter(None, array_of_array))
    for arr in arrays:
        arr_filtered = list(filter(None, arr))
        res.extend(arr_filtered)
    return res


def test_Should_inherit_adapter_base_When_checked_for_subclass():
    assert issubclass(IniAdapter, AdapterBase)


def _get_filepath_combinations():
    default_file_path_options = [None, ["default.ini"]]
    constructor_file_path_options = [None, ["constructor.ini"]]
    configuration_file_path_options = [None, ["configuration.ini"]]
    return [
        (default_file_path, constructor_file_path, configuration_file_path)
        for default_file_path in default_file_path_options
        for constructor_file_path in constructor_file_path_options
        for configuration_file_path in configuration_file_path_options
    ]


def _get_filepath_combinations_with_constructor_override():
    default_file_path_options = [None, ["default.ini"]]
    constructor_file_path_options = [None, ["constructor.ini"]]
    configuration_file_path_options = [None, ["configuration.ini"]]
    return [
        (
            default_file_path,
            constructor_file_path,
            configuration_file_path,
            constructor_override,
        )
        for default_file_path in default_file_path_options
        for constructor_file_path in constructor_file_path_options
        for configuration_file_path in configuration_file_path_options
        for constructor_override in [True, False]
    ]


@pytest.mark.parametrize(
    "default_file_path, constructor_file_path, configuration_file_path",
    _get_filepath_combinations(),
)
def test_Should_match_expected_file_paths_When_file_paths_specified_at_different_levels(
    field_decorated_callable,
    configparser,
    default_file_path,
    constructor_file_path,
    configuration_file_path,
):
    IniAdapter.set_default_ini_files(default_file_path)
    adapter = IniAdapter("section_a", file_names=constructor_file_path)
    configured_callable = IniAdapter.configure(file_paths=configuration_file_path)(
        field_decorated_callable
    )
    expected_file_paths = _flatten_array(
        [default_file_path, constructor_file_path, configuration_file_path]
    )
    if len(expected_file_paths) == 0:
        with pytest.raises(ValueError):
            _ = adapter.get_field("option_a", configured_callable)
        return
    _ = adapter.get_field("option_a", configured_callable)
    configparser.return_value.read.assert_called_once_with(expected_file_paths)


@pytest.mark.parametrize(
    "default_file_path, constructor_file_path, configuration_file_path",
    _get_filepath_combinations(),
)
def test_Should_ignore_default_file_paths_When_constructor_override_file_is_true(
    field_decorated_callable,
    configparser,
    default_file_path,
    constructor_file_path,
    configuration_file_path,
):
    IniAdapter.set_default_ini_files(default_file_path)
    adapter = IniAdapter(
        "section_a", file_names=constructor_file_path, override_files=True
    )
    configured_callable = IniAdapter.configure(file_paths=configuration_file_path)(
        field_decorated_callable
    )
    expected_file_paths = _flatten_array(
        [constructor_file_path, configuration_file_path]
    )
    if len(expected_file_paths) == 0:
        with pytest.raises(ValueError):
            _ = adapter.get_field("option_a", configured_callable)
        return
    _ = adapter.get_field("option_a", configured_callable)
    configparser.return_value.read.assert_called_once_with(expected_file_paths)


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    "default_file_path, constructor_file_path, configuration_file_path, constructor_override",
    _get_filepath_combinations_with_constructor_override(),
)
def test_Should_ignore_default_and_constructor_file_paths_When_configuration_override_is_true(
    field_decorated_callable,
    configparser,
    default_file_path,
    constructor_file_path,
    configuration_file_path,
    constructor_override,
):
    IniAdapter.set_default_ini_files(default_file_path)
    adapter = IniAdapter(
        section_name="section_a",
        file_names=constructor_file_path,
        override_files=constructor_override,
    )
    configured_callable = IniAdapter.configure(
        file_paths=configuration_file_path, override_files=True
    )(field_decorated_callable)
    expected_file_paths = _flatten_array([configuration_file_path])
    if len(expected_file_paths) == 0:
        with pytest.raises(ValueError):
            _ = adapter.get_field("option_a", configured_callable)
        return
    _ = adapter.get_field("option_a", configured_callable)
    configparser.return_value.read.assert_called_once_with(expected_file_paths)


@pytest.mark.parametrize("section_name", [None, "section_a", "Section_A"])
def test_Should_use_constructor_section_name_When_looking_config_parser(
    field_decorated_callable, configparser, section_name
):
    adapter = IniAdapter(section_name)
    configured_callable = IniAdapter.configure()(field_decorated_callable)
    if section_name is None:
        with pytest.raises(ValueError):
            _ = adapter.get_field("option_a", configured_callable)
        return
    _ = adapter.get_field("option_a", configured_callable)
    configparser.return_value.get.assert_called_once_with(section_name, "option_a")


@pytest.mark.parametrize(
    "constructor_section_name, configuration_section_name",
    [
        (None, None),
        ("section_a", None),
        (None, "section_a"),
        ("section_a", "section_b"),
    ],
)
def test_Should_use_configuration_section_name_When_specified(
    field_decorated_callable,
    configparser,
    constructor_section_name,
    configuration_section_name,
):
    IniAdapter.set_default_ini_files(["default.ini"])
    adapter = IniAdapter(constructor_section_name)
    configured_callable = IniAdapter.configure(section_name=configuration_section_name)(
        field_decorated_callable
    )
    expected_section_name = configuration_section_name or constructor_section_name
    if expected_section_name is None:
        with pytest.raises(ValueError):
            _ = adapter.get_field("option_a", configured_callable)
        return
    _ = adapter.get_field("option_a", configured_callable)
    configparser.return_value.get.assert_called_once_with(
        expected_section_name, "option_a"
    )


@pytest.mark.parametrize(
    "field_name, option_name",
    [
        ("stub_field", None),
        ("stub_field", "stub_config_field"),
        ("Stub_Field", "Stub_Config_field"),
    ],
)
def test_Should_use_configuration_field_name_When_specified(
    field_decorated_callable, configparser, field_name, option_name
):
    IniAdapter.set_default_ini_files(["default.ini"])
    adapter = IniAdapter("section_a")
    configured_callable = IniAdapter.configure(option_name=option_name)(
        field_decorated_callable
    )
    expected_field_name = option_name or field_name
    _ = adapter.get_field(field_name, configured_callable)
    configparser.return_value.get.assert_called_once_with(
        "section_a", expected_field_name
    )


def test_Should_use_field_and_constructor_args_When_configuration_is_not_specified(
    field_decorated_callable, configparser
):
    IniAdapter.set_default_ini_files(["default.ini"])
    adapter = IniAdapter("section_a")
    _ = adapter.get_field("stub_field", field_decorated_callable)
    configparser.return_value.get.assert_called_once_with("section_a", "stub_field")


def test_Should_raise_adapter_error_When_section_or_option_is_not_found(
    field_decorated_callable, configparser
):
    configparser.return_value.get.side_effect = NoOptionError("option_a", "section_a")
    IniAdapter.set_default_ini_files(["default.ini"])
    adapter = IniAdapter("section_a")
    with pytest.raises(AdapterError) as e:
        _ = adapter.get_field("option_a", field_decorated_callable)
    assert "Field option_a not found in section_a section of ['default.ini']" in str(e)


def test_Should_return_option_value_When_found(field_decorated_callable, configparser):
    configparser.return_value.get.return_value = "option_a_value"
    adapter = IniAdapter("section_a", file_names=["default.ini"])
    result = adapter.get_field("option_a", field_decorated_callable)
    assert result == "option_a_value"
    configparser.return_value.get.assert_called_once_with("section_a", "option_a")
