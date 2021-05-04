
# Copyright 2020, Battelle Energy Alliance, LLC
# ALL RIGHTS RESERVED

from utils import InputData, InputTypes
from EntityFactoryBase import EntityFactory

from .SyntheticHistory import SyntheticHistory
from .Function import Function
from .Parametric import Parametric, FixedValue, OptBounds, SweepValues
from .Linear import Linear
from .Variable import Variable

class ValuedParamFactory(EntityFactory):
  """
    Factory for ValuedParams
  """
  def __init__(self, *args):
    """
      Instantiate
      @ In, args, list, positional arguments
      @ Out, None
    """
    super().__init__(*args)
    # TODO registered_entities = [] # for filling in values

  def make_input_specs(self, name, descr=None, allowed=None, kind='singular'):
    """
      Fill input specs for the provided name and description.
      @ In, name, str, name of new spec
      @ In, descr, str, optional, description of spec
      @ In, allowed, list, optional, string list of allowable types of ValuedParam. Overrides "kind".
      @ In, kind, str, optional, kind of ValuedParam grouping (default)
      @ Out, spec, InputData, specification
    """
    if allowed is None:
      allowed = allowable[kind]
    allowed_str = ', '.join(['\\xmlNode{{{}}}'.format(a) for a in allowed])
    add_descr = rf"""This value can be taken from any \emph{{one}} of the sources as subnodes
                (described below): {allowed_str}."""
    if descr is None:
      description = add_descr
    else:
      description = descr + r"""\\ \\""" + add_descr
    spec = InputData.parameterInputFactory(name, descr=description)
    for typ, klass in self._registeredTypes.items():
      if typ in allowed:
        spec.addSub(klass.get_input_specs())
    # addons
    spec.addSub(InputData.parameterInputFactory('multiplier', contentType=InputTypes.FloatType,
        descr=r"""Multiplies any value obtained by this parameter by the given value. \default{1}"""))
    return spec

factory = ValuedParamFactory('ValuedParam')

# fixed in inner
factory.registerType('fixed_value', FixedValue)
factory.registerType('sweep_values', SweepValues)
factory.registerType('opt_bounds', OptBounds)
factory.registerType('variable', Variable)
# frequent revaluation
factory.registerType('ARMA', SyntheticHistory)
factory.registerType('Function', Function)
# ratios, transfers
factory.registerType('linear', Linear)
# TODO are transfer functions and valued evaluations really the same creature?
# TODO add: activity, ROM

# map of "kinds" of ValuedParams to the default acceptable ValuedParam types
allowable = {
  # transfer functions, such as producing components' transfer functions
  'transfer': ['linear', 'Function'],
  # single evaluations, like cashflow prices and component capacities
  'singular': ['fixed_value', 'sweep_values', 'opt_bounds', 'variable', 'ARMA', 'Function'],
  # all
  'all': list(factory.knownTypes()),
}
