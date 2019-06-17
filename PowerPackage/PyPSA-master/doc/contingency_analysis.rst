######################
Contingency Analysis
######################


See the module ``pypsa.contingency``.

Contingency analysis is concerned with the behaviour of the power
system after contingencies such as the outage of particular branches.
Only branch outages and the resulting effects on linear power flow are
considered here; extensions for non-linear power flow and generator
outages may be added in the future.


Branch Outage Distribution Factors (BODF)
=========================================

``sub_network.caculate_BODF()`` calculates the matrix of Branch Outage
Distribution Factors (BODF) and stores it as
``sub_network.BODF``. (BODF are also called Line Outage Distribution
Factors (LODF) in the literature, but in PyPSA other passive branches
such as transformers are also included.)

The BODF gives the change of flow on the branches in the network
following a branch outage, based on the linear power flow.

For the outage of branch :math:`c`, let :math:`f_b` be the flows
before the outage and :math:`f_b^{(c)}` be the flows after the
outage. Then the BODF is defined by

.. math::
   f_b^{(c)} = f_b + BODF_{bc}f_{c}


The BODF can be computed fairly directly from the Power Transfer
Distribution Factors (PTDF). First build the branch PTDF :math:`BPTDF`
from the PTDF and incidence matrix :math:`K`

.. math::
   BPTDF_{bc} = \sum_{i} PTDF_{bi} K_{ic}

:math:`BPTDF_{bc}` gives the change in flow on branch :math:`b` if a
unit of power is injected at the from-bus of branch :math:`c` and
withdrawn from the to-bus of branch :math:`c`. If branch :math:`b` is
the only branch connecting two regions, then :math:`BPTDF_{bb} = 1`,
since the power can only flow between the two ends of the branch
through the branch itself.

The off-diagonal entries of the BODF :math:`b \neq c`  are given by:

.. math::
   BODF_{bc} = \frac{BPTDF_{bc}}{1-BPTDF_{cc}}

If :math:`c` is the only branch connecting two regions, so that the
regions become disconnected after the outage of :math:`c`, then
:math:`BPTDF_{cc} = 1` and :math:`BODF_{bc}` becomes singular; this
case must be treated separately since, for example, each region will
need its own slack.

The diagonal entries of the BODF are simply:

.. math::
   BODF_{bb} = -1



Linear Power Flow Contingency Analysis
======================================

``network.lpf_contingency(snapshot, branch_outages)`` computes a base
case linear power flow (LPF) with no outages for ``snapshot``, and
then cycles through the list of branches in ``branch_outages`` and
computes the line flows after the outage of that branch using the BODF.

The function returns a pandas.DataFrame ``p0`` with the flows in each
case in each column of the DataFrame.



Security-Constrained Linear Optimal Power Flow (SCLOPF)
=======================================================

The Security-Constrained Linear Optimal Power Flow (SCLOPF) builds on
the Linear Optimal Power Flow (LOPF) described in
:doc:`optimal_power_flow` by including additional constraints that
branches may not become overloaded after the outage of a selection of
branches.

The SCLOPF is called with the method::

    network.sclopf(snapshots,branch_outages,**kwargs)

where ``branch_outages`` is a list of the branches whose outages
should not overload the network. ``**kwargs`` are all the same
arguments that may be passed to ``network.lopf()``. (Note that
``network.sclopf()`` is implemented by adding a function to
``network.lopf()`` via the ``extra_functionality`` keyword.)


For each potential outage of a branch :math:`c` add a set of
constraints for all other branches :math:`b` in the sub-network that
they do not become overloaded beyond their capacity :math:`F_b`:


.. math::
   |f_{b,t}^{(c)}| = |f_{b,t} + BODF_{bc}f_{c,t}| \leq |F_b| \hspace{1cm} \forall b


This applies for all snapshots :math:`t` considered in the optimisation.




Inputs and Outputs
------------------

See LOPF in :doc:`optimal_power_flow`.
