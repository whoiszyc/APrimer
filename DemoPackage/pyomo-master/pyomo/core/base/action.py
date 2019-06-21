#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright 2017 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and 
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain 
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

__all__ = ['BuildAction']

import logging
import types

from pyomo.common.timing import ConstructionTimer
from pyomo.core.base.plugin import ModelComponentFactory
from pyomo.core.base.indexed_component import IndexedComponent
from pyomo.core.base.misc import apply_indexed_rule

logger = logging.getLogger('pyomo.core')


@ModelComponentFactory.register("A component that performs arbitrary actions during model construction.  The action rule is applied to every index value.")
class BuildAction(IndexedComponent):
    """A build action, which executes a rule for all valid indices.

    Constructor arguments:
        rule        The rule that is executed for every indice.

    Private class attributes:
        _rule       The rule that is executed for every indice.
    """

    def __init__(self, *args, **kwd):
        self._rule = kwd.pop('rule', None)
        kwd['ctype'] = BuildAction
        IndexedComponent.__init__(self, *args, **kwd)
        #
        if not type(self._rule) is types.FunctionType:
            raise ValueError("BuildAction must have an 'rule' option specified whose value is a function")

    def _pprint(self):
        return ([("Size", len(self)),
                 ("Index", self._index if self.is_indexed() else None),
                 ("Active", self.active),]
                 , None, None, None)

    def construct(self, data=None):
        """ Apply the rule to construct values in this set """
        if __debug__ and logger.isEnabledFor(logging.DEBUG):   #pragma:nocover
            logger.debug("Constructing Action, name="+self.name)
        #
        if self._constructed:                                  #pragma:nocover
            return
        timer = ConstructionTimer(self)
        self._constructed=True
        #
        if not self.is_indexed():
            # Scalar component
            self._rule(self._parent())
        else:
            # Indexed component
            for index in self._index:
                apply_indexed_rule(self, self._rule, self._parent(), index)
        timer.report()
