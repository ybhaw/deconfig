from unittest.mock import MagicMock

import pytest

from deconfig.core import AdapterBase, EnvAdapter, AdapterError


@pytest.mark.parametrize(
    "import_name",
    [
        "field", "optional", "validate", "add_adapter",
        "set_default_adapters", "config", "transform",
        "EnvAdapter", "IniAdapter"
    ],
    ids=[
        "field", "optional", "validate", "add_adapter",
        "set_default_adapters", "config", "transform",
        "EnvAdapter", "IniAdapter"
    ]
)
def test_Should_have_expected_field_When_deconfig_is_imported(import_name):
    import deconfig
    assert hasattr(deconfig, import_name)


class TestField:

    def test_Should_raise_TypeError_When_argument_is_not_string(self):
        from deconfig import field

        class NotString:
            def __str__(self):
                raise TypeError("Not a string")

        with pytest.raises(TypeError):
            @field(NotString())
            def test_field():
                pass

    def test_Should_set_attribute_name_When_field_is_called(self):
        from deconfig import field

        @field("test")
        def test_field():
            pass

        assert hasattr(test_field, "name")
        assert test_field.name == "test"

    def test_Should_set_attribute_adapter_configs_When_field_is_called(self):
        import deconfig
        mock_field = MagicMock()
        response = deconfig.field("test")(mock_field)
        assert hasattr(response, "adapter_configs")

    def test_Should_return_same_function_When_field_is_called(self):
        from deconfig import field
        mock = MagicMock()
        response_callback = field("test")(mock)
        assert response_callback == mock


class TestOptional:
    def test_Should_set_attribute_optional_When_optional_is_called(self):
        from deconfig import optional

        @optional()
        def test_optional():
            pass

        assert hasattr(test_optional, "optional")
        assert test_optional.optional is True

    def test_Should_return_same_function_When_optional_is_called(self):
        from deconfig import optional
        mock = MagicMock()
        response_callback = optional()(mock)
        assert response_callback == mock

    def test_Should_set_attribute_optional_to_True_When_optional_is_called_with_True(self):
        from deconfig import optional

        @optional(True)
        def test_optional():
            pass

        assert hasattr(test_optional, "optional")
        assert test_optional.optional is True

    def test_Should_set_attribute_optional_to_False_When_optional_is_called_with_False(self):
        from deconfig import optional

        @optional(False)
        def test_optional():
            pass

        assert hasattr(test_optional, "optional")
        assert test_optional.optional is False

    def test_Should_not_raise_TypeError_When_argument_cannot_be_cast_to_bool(self):
        from deconfig import optional

        class NotBool:
            def __bool__(self):
                raise TypeError("Not a bool")

        with pytest.raises(TypeError):
            @optional(NotBool())
            def test_optional():
                pass


class TestValidationCallback:

    def test_Should_set_attribute_validation_callback_When_validate_is_called(self):
        from deconfig import validate

        def mock_validation_callback():
            pass

        @validate(mock_validation_callback)
        def test_validate():
            pass

        assert hasattr(test_validate, "validation_callback")
        assert test_validate.validation_callback == mock_validation_callback

    def test_Should_return_same_function_When_validate_is_called(self):
        from deconfig import validate
        mock = MagicMock()
        response_callback = validate(mock)(mock)
        assert response_callback == mock

    def test_Should_raise_TypeError_When_argument_is_None(self):
        from deconfig import validate
        with pytest.raises(TypeError):
            @validate(None)
            def test_validate():
                pass

    def test_Should_raise_TypeError_When_argument_is_not_callable(self):
        from deconfig import validate
        with pytest.raises(TypeError):
            @validate(1)
            def test_validate():
                pass


class TestAddAdapter:
    def test_Should_set_attribute_adapters_When_add_adapter_is_called(self):
        from deconfig import add_adapter

        mock_adapter = MagicMock(AdapterBase)

        @add_adapter(mock_adapter())
        def get_field_with_added_adapter():
            pass

        assert hasattr(get_field_with_added_adapter, "adapters")
        assert get_field_with_added_adapter.adapters == [mock_adapter.return_value]

    def test_Should_return_same_function_When_add_adapter_is_called(self):
        from deconfig import add_adapter

        mock = MagicMock(AdapterBase)
        response_callback = add_adapter(mock)(mock)
        assert response_callback == mock

    def test_Should_add_adapter_to_existing_adapters_When_add_adapter_is_called(self):
        from deconfig import add_adapter

        adapter_1 = MagicMock(AdapterBase)
        field_mock = MagicMock()
        field_mock.adapters = [adapter_1.return_value]

        adapter_2 = MagicMock(AdapterBase)
        field_mock_with_decorator = add_adapter(adapter_2())(field_mock)
        assert hasattr(field_mock_with_decorator, "adapters")
        assert field_mock_with_decorator.adapters == [adapter_2.return_value, adapter_1.return_value]

        adapter_3 = MagicMock(AdapterBase)
        field_mock_with_third_adapter = add_adapter(adapter_3())(field_mock_with_decorator)
        assert hasattr(field_mock_with_third_adapter, "adapters")
        assert field_mock_with_third_adapter.adapters == [adapter_3.return_value, adapter_2.return_value,
                                                          adapter_1.return_value]

    def test_Should_add_adapter_as_new_list_When_add_adapter_is_called(self):
        from deconfig import add_adapter

        mock_adapter = MagicMock(AdapterBase)

        def field_stub():
            pass

        assert not hasattr(field_stub, "adapters")

        field_decorated = add_adapter(mock_adapter())(field_stub)
        assert hasattr(field_decorated, "adapters")
        assert field_decorated.adapters == [mock_adapter.return_value]

    def test_Should_raise_ValueError_When_argument_is_None(self):
        from deconfig import add_adapter
        with pytest.raises(TypeError):
            @add_adapter(None)
            def test_add_adapter():
                pass

    def test_Should_raise_ValueError_When_argument_is_not_AdapterBase(self):
        from deconfig import add_adapter
        with pytest.raises(TypeError):
            @add_adapter(1)
            def test_add_adapter():
                pass


class TestSetDefaultAdapters:
    def test_Should_set_default_adapters_to_EnvAdapter_When_set_default_adapters_is_not_called(self):
        # noinspection PyProtectedMember
        from deconfig import _adapters, config, field

        assert len(_adapters) == 1
        assert isinstance(_adapters[0], EnvAdapter)
        mocked_adapter = MagicMock(AdapterBase)
        config_response = MagicMock("config_response")
        mocked_adapter.get_field.return_value = config_response
        _adapters.insert(0, mocked_adapter)

        @config()
        class TestConfig:
            @field(name="test")
            def test_field(self):
                pass

        test_config = TestConfig()
        assert test_config.test_field() == config_response

    def test_Should_raise_TypeError_When_set_default_adapters_is_called_with_no_adapters(self):
        from deconfig import set_default_adapters
        with pytest.raises(TypeError):
            set_default_adapters()

    def test_Should_raise_TypeError_When_set_default_adapters_is_called_with_non_AdapterBase(self):
        from deconfig import set_default_adapters, EnvAdapter
        with pytest.raises(TypeError):
            set_default_adapters(1)
        with pytest.raises(TypeError):
            set_default_adapters(EnvAdapter(), 1)

    def test_Should_set_default_adapters_to_given_adapters_When_set_default_adapters_is_called_with_adapters(self):
        from deconfig import config, field, set_default_adapters
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        set_default_adapters(adapter)

        @config()
        class MockConfig:
            @field(name="field")
            def test_field(self):
                pass

        config = MockConfig()
        assert config.test_field() == adapter_response


class TestConfig:
    def test_Should_use_env_adapter_When_no_adapters_are_set(self):
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response
        import deconfig
        deconfig._adapters = [adapter]

        from deconfig import config, field

        @config()
        class ConfigStub:
            @field(name="test")
            def field_stub(self):
                pass

        config = ConfigStub()
        assert config.field_stub() == adapter_response

    def test_Should_update_and_use_class_adapters_When_adapters_set_using_decorator_args(self):
        from deconfig import config, field
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        @config([adapter])
        class ConfigStub:
            @field(name="test")
            def field_stub(self):
                pass

        config = ConfigStub()
        assert config.field_stub() == adapter_response

    def test_Should_update_and_use_class_adapters_When_adapters_set_using_set_default_adapters(self):
        from deconfig import config, field, set_default_adapters
        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        set_default_adapters(adapter)

        @config()
        class ConfigStub:
            @field(name="test")
            def field_stub(self):
                pass

        config = ConfigStub()
        assert config.field_stub() == adapter_response

    def test_Should_prioritize_config_args_When_config_has_adapters_and_default_is_also_set(self):
        from deconfig import config, field, set_default_adapters

        default_adapter = MagicMock(AdapterBase)

        arg_adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        arg_adapter.get_field.return_value = adapter_response

        set_default_adapters(default_adapter)

        @config([arg_adapter])
        class ConfigStub:
            @field(name="test")
            def field_stub(self):
                pass

        config = ConfigStub()
        assert config.field_stub() == adapter_response

    def test_Should_only_configure_methods_with_field_decorator_When_config_is_called(self):
        from deconfig import config, field

        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        @config(adapters=[adapter])
        class ConfigStub:
            def method_without_field_decorator(self):
                return 1

            @field(name="test")
            def method_with_field_decorator(self):
                return 2

        config = ConfigStub()
        assert config.method_with_field_decorator() == adapter_response
        assert config.method_without_field_decorator() == 1
        assert adapter.get_field.call_count == 1

    def test_Should_prioritize_methods_adapters_When_method_has_adapters(self):
        from deconfig import config, field, add_adapter

        method_adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        method_adapter.get_field.return_value = adapter_response

        class_adapter = MagicMock(AdapterBase)
        default_adapter_response = MagicMock("default_adapter_response")
        class_adapter.get_field.return_value = default_adapter_response

        @config(adapters=[class_adapter])
        class ConfigStub:
            @add_adapter(method_adapter)
            @field(name="test")
            def method_with_field_adapter(self):
                return 2

            @field(name="test_2")
            def method_without_field_decorator(self):
                return 2

        config = ConfigStub()
        assert config.method_with_field_adapter() == adapter_response
        assert config.method_without_field_decorator() == default_adapter_response
        assert method_adapter.get_field.call_count == 1
        assert class_adapter.get_field.call_count == 1

    def test_Should_use_class_adapters_When_field_missing_in_field_adapters(self):
        from deconfig import config, field, add_adapter

        method_adapter = MagicMock(AdapterBase)
        method_adapter.get_field.side_effect = AdapterError("Intentional error")

        class_adapter = MagicMock(AdapterBase)
        default_adapter_response = MagicMock("default_adapter_response")
        class_adapter.get_field.return_value = default_adapter_response

        @config(adapters=[class_adapter])
        class ConfigStub:
            @add_adapter(method_adapter)
            @field(name="test")
            def method_with_field_adapter(self):
                return 2

            @field(name="test_2")
            def method_without_field_decorator(self):
                return 2

        config = ConfigStub()
        assert config.method_with_field_adapter() == default_adapter_response
        assert method_adapter.get_field.call_count == 1
        assert class_adapter.get_field.call_count == 1

    def test_Should_update_field_methods_with_decorated_config_decorator_When_class_is_decorated_with_config(self):
        from deconfig import config, field

        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        @config([adapter])
        class ConfigStub:
            @field(name="test")
            def field_stub(self):
                pass

        config = ConfigStub()
        assert config.field_stub() == adapter_response
        assert config.field_stub.__name__ == "decorated_config_wrapper"

    def test_Should_add_reset_deconfig_cache_method_When_class_is_decorated_with_config(self):
        from deconfig import config, field

        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        @config([adapter])
        class ConfigStub:
            @field(name="test")
            def field_stub(self):
                pass

        config = ConfigStub()
        config.field_stub()
        assert hasattr(config, "reset_deconfig_cache")
        assert callable(config.reset_deconfig_cache)
        config.reset_deconfig_cache()

    def test_Should_not_create_reset_deconfig_cache_When_class_already_has_reset_deconfig_cache_method(self):
        from deconfig import config, field

        adapter = MagicMock(AdapterBase)
        adapter_response = MagicMock("adapter_response")
        adapter.get_field.return_value = adapter_response

        config_cache_stub = MagicMock()

        @config([adapter])
        class ConfigStub:
            @field(name="test")
            def field_stub(self):
                pass

            def reset_deconfig_cache(self):
                return config_cache_stub

        config = ConfigStub()
        assert hasattr(config, "reset_deconfig_cache")
        assert config.reset_deconfig_cache() == config_cache_stub


class TestDecoratedConfigDecorator:
    def test_Should_raise_ValueError_When_field_name_is_not_present(self):
        def callable_stub():
            pass

        with pytest.raises(ValueError) as e:
            from deconfig import decorated_config_decorator
            decorated_config_decorator(callable_stub)
        assert str(e.value) == "Have you forgotten to decorate field with @field(name='name')?"

    def test_Should_raise_ValueError_When_adapters_are_not_present(self):
        def callable_stub():
            pass

        callable_stub.name = "test"
        with pytest.raises(ValueError) as e:
            from deconfig import decorated_config_decorator
            decorated_config_decorator(callable_stub)
        assert str(e.value) == "Class not decorated with @config"

    def test_Should_mandate_field_be_present_in_config_False_When_optional_is_not_set_or_is_False(self):
        from deconfig import decorated_config_decorator

        adapter = MagicMock()
        adapter.get_field.side_effect = AdapterError("Value not found")

        callable_stub_without_optional = lambda x: None
        callable_stub_without_optional.name = "test"
        callable_stub_without_optional.adapters = [adapter]
        response_callback = decorated_config_decorator(callable_stub_without_optional)
        with pytest.raises(ValueError) as e:
            response_callback()
        assert str(e.value) == "Field test not found in any config."

        callable_stub_with_optional_false = lambda x: None
        callable_stub_with_optional_false.name = "test_2"
        callable_stub_with_optional_false.adapters = [adapter]
        callable_stub_with_optional_false.optional = False
        response_callback = decorated_config_decorator(callable_stub_with_optional_false)
        with pytest.raises(ValueError) as e:
            response_callback()
        assert str(e.value) == "Field test_2 not found in any config."

    def test_Should_set_optional_to_True_When_optional_is_set_to_true(self):
        from deconfig import decorated_config_decorator

        adapter = MagicMock()
        adapter.get_field.side_effect = AdapterError("Value not found")

        callable_stub = lambda: None
        callable_stub.name = "test"
        callable_stub.adapters = [adapter]
        callable_stub.optional = True
        response = decorated_config_decorator(callable_stub)
        assert response() is None

    def test_Should_call_validation_callback_When_set(self):
        from deconfig import decorated_config_decorator

        adapter = MagicMock()
        adapter.get_field.return_value = 1

        validation_callback = MagicMock()
        callable_stub = lambda: None
        callable_stub.name = "test"
        callable_stub.adapters = [adapter]
        callable_stub.validation_callback = validation_callback
        response = decorated_config_decorator(callable_stub)
        response()
        validation_callback.assert_called_once_with(1)

    def test_Should_raise_ValueError_When_validation_callback_raises_error(self):
        from deconfig import decorated_config_decorator

        adapter = MagicMock()
        validation_callback = MagicMock()
        validation_callback.side_effect = ValueError("Validation error")
        callable_stub = lambda: None
        callable_stub.name = "test"
        callable_stub.adapters = [adapter]
        callable_stub.validation_callback = validation_callback
        response = decorated_config_decorator(callable_stub)
        with pytest.raises(ValueError) as e:
            response()
        validation_callback.assert_called_once_with(adapter.get_field.return_value)
        assert str(e.value) == "Validation error"

    def test_Should_call_transform_callback_When_set(self):
        from deconfig import decorated_config_decorator

        adapter = MagicMock()
        adapter.get_field.return_value = 1

        transform_callback = MagicMock()
        transform_callback.return_value = 2
        callable_stub = lambda: None
        callable_stub.name = "test"
        callable_stub.adapters = [adapter]
        callable_stub.transform_callback = transform_callback
        response = decorated_config_decorator(callable_stub)
        assert response() == 2
        transform_callback.assert_called_once_with(1)

    def test_Should_cache_transformed_response_When_invoked_and_has_transformer(self):
        from deconfig import decorated_config_decorator
        adapter = MagicMock()
        adapter.get_field.side_effect = [1]
        callable_stub = lambda: None
        callable_stub.name = "test"
        callable_stub.adapters = [adapter]
        transform_callback = MagicMock()
        callable_stub.transform_callback = transform_callback
        response = decorated_config_decorator(callable_stub)
        assert response() == transform_callback.return_value
        assert response() == transform_callback.return_value
        assert transform_callback.call_count == 1

    def test_Should_cache_response_When_invoked(self):
        from deconfig import decorated_config_decorator
        adapter = MagicMock()
        adapter.get_field.side_effect = [1]
        callable_stub = lambda: None
        callable_stub.name = "test"
        callable_stub.adapters = [adapter]
        response = decorated_config_decorator(callable_stub)
        assert response() == 1
        assert response() == 1
        assert adapter.get_field.call_count == 1

    def test_Should_rebuild_value_When_cache_reset_using_reset_deconfig_cache(self):
        from deconfig import config, field

        adapter = MagicMock(AdapterBase)
        adapter.get_field.side_effect = [1, 2]

        @config([adapter])
        class ConfigStub:
            @field(name="test")
            def field_stub(self):
                pass

        config = ConfigStub()
        assert config.field_stub() == 1
        assert config.field_stub() == 1
        assert adapter.get_field.call_count == 1
        config.reset_deconfig_cache()
        assert config.field_stub() == 2
        assert config.field_stub() == 2
        assert adapter.get_field.call_count == 2

    def test_Should_call_adapters_in_sequence_When_invoked(self):
        from deconfig import decorated_config_decorator

        adapter_1 = MagicMock(AdapterBase)
        adapter_2 = MagicMock(AdapterBase)
        adapter_3 = MagicMock(AdapterBase)
        adapter_1.get_field.side_effect = AdapterError("Value not found")
        adapter_2.get_field.side_effect = [1]
        adapter_3.get_field.side_effect = [None]

        callable_stub = lambda: None
        callable_stub.name = "test"
        callable_stub.adapters = [adapter_1, adapter_2, adapter_3]
        response = decorated_config_decorator(callable_stub)
        response()
        assert adapter_1.get_field.call_count == 1
        assert adapter_2.get_field.call_count == 1
        assert adapter_3.get_field.call_count == 0
