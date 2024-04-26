# <span style="color:#cb09d7">De</span><span style="color: #635ec4">co</span><span style="color:#c7fe59">nfig</span>

<b><span style="color:#cb09d7">Decorator </span>
<span style="color:#635ec4">+</span>
<span style="color:#c7fe59">Config</span></b>

This is just another <b>configuration library</b> for Python. Create
configuration objects and initialize them with data from different
sources. It is designed to be extensible, and provides lots of features
that are commonly used when dealing with configurations.

## Installation

```bash
pip install deconfig
```

## Quick Start

```python
import deconfig as de
import os

os.environ["FOO"] = "bar"

# Deconfig uses EnvAdapter by default,
# but you can change this behaviour as follows:
de.set_default_adapters(de.EnvAdapter())


@de.config()
class ExampleConfig:

    @de.transformer.string() # Cast value to string
    @de.optional()           # Field can be null
    @de.field(name="foo")    # use name "foo" in configuration files
    def get_foo(self):
        pass


config = ExampleConfig()
config.get_foo() # Returns "bar"
```

## Features

### Optional

By default, deconfig considers all fields as required. But you can
mark a field as optional by using the `@de.optional()` decorator.

```python
import deconfig as de

@de.config(adapters=[de.EnvAdapter()])
class ExampleConfig:
    @de.optional()
    @de.field(name="foo")
    def get_foo(self):
        pass

    @de.field(name="bar")
    def get_bar(self):
        pass

config = ExampleConfig()
config.get_foo() # Returns None
config.get_bar() # Raises ValueError
```

### Transformers

Configuration files can be very limiting. But with transformers, you can
transform the value to any type/format you want.

```python
import deconfig as de

capitalize = lambda x: x.capitalize()

@de.config(adapters=[de.EnvAdapter()])
class ExampleConfig:
    @de.transformer.integer()
    @de.field(name="foo")
    def get_foo(self):
        return "1"

    @de.transformer.comma_separated_array_string(str)
    @de.field(name="bar")
    def get_bar(self):
        return "default,values"

    @de.transformer.cast_custom(capitalize)
    @de.field(name="baz")
    def get_baz(self):
        return "hello"


config = ExampleConfig()
config.get_foo() # Returns 1
config.get_bar() # Returns ["default", "values"]
config.get_baz() # Returns "Hello"
```

### Validator callbacks

You can also add custom validation logic to your fields.

```python
import deconfig as de

def is_even(value) -> None:
    if not value % 2:
        raise ValueError("Value must be even")

@de.config(adapters=[de.EnvAdapter()])
class ExampleConfig:
    @de.validate(is_even)
    @de.field(name="foo")
    def get_foo(self):
        return 2

    @de.validate(is_even)
    @de.field(name="bar")
    def get_bar(self):
        return 3

config = ExampleConfig()
config.get_foo() # Returns 2
config.get_bar() # Raises ValueError
```

## Customizations

Adapters are used to load data from different sources. By default,
deconfig ships with adapter for environment variables and ini files.
You can also create your own adapter for your custom use case.

Here is a pseudo adapter that sets all values to method name:

```python
from typing import *
import deconfig as de

T = TypeVar("T")

class FooAdapter(de.AdapterBase):

    def get_field(self, field_name: str, method: Callable[..., T], *method_args, **method_kwargs) -> Any:
        return method.__name__
```


## Read More

There is a lot more of options and features that you can use with
deconfig. Check out the documentation for more information.

- [Documentation](https://deconfig.readthedocs.io) # TODO
- [GitHub](https://github.com/ybhaw/deconfig.git) # TODO
