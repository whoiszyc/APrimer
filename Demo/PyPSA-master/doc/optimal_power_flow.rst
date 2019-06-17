######################
 Optimal Power Flow
######################


See the module ``pypsa.opf``.


Non-Linear Optimal Power Flow
==============================

Optimisation with the full non-linear power flow equations is not yet
supported.



Linear Optimal Power Flow
=========================

Optimisation with the linearised power flow equations for (mixed) AC
and DC networks is fully supported.

All constraints and variables are listed below.


Overview
--------
Execute:


``network.lopf(snapshots, solver_name="glpk", solver_io=None,
extra_functionality=None, solver_options={}, keep_files=False,
formulation="angles",extra_postprocessing=None)``

where ``snapshots`` is an iterable of snapshots, ``solver_name`` is a
string, e.g. "gurobi" or "glpk", ``solver_io`` is a string,
``extra_functionality`` is a function of network and snapshots that is
called before the solver (see below), ``extra_postprocessing`` is a
function of network, snapshots and duals that is called after solving
(see below), ``solver_options`` is a dictionary of flags to pass to
the solver, ``keep_files`` means that the ``.lp`` file is saved and
``formulation`` is a string in
``["angles","cycles","kirchhoff","ptdf"]`` (see :ref:`formulations`
for more details).

The linear OPF module can optimises the dispatch of generation and storage
and the capacities of generation, storage and transmission.

It is assumed that the load is inelastic and must be met in every
snapshot (this will be relaxed in future versions).

The optimisation currently uses continuous variables for most
functionality; unit commitment with binary variables is also
implemented for generators.

The objective function is the total system cost for the snapshots
optimised.

Each snapshot can be given a weighting :math:`w_t` to represent
e.g. multiple hours.

This set-up can also be used for stochastic optimisation, if you
interpret the weighting as a probability.

Each transmission asset has a capital cost.

Each generation and storage asset has a capital cost and a marginal cost.


WARNING: If the transmission capacity is changed in passive networks,
then the impedance will also change (i.e. if parallel lines are
installed). This is NOT reflected in the LOPF, so the network
equations may no longer be valid. Note also that all the expansion is
continuous.


Optimising dispatch only: a market model
----------------------------------------

Capacity optimisation can be turned off so that only the dispatch is
optimised, like a short-run electricity market model.

For simplified transmission representation using Net Transfer
Capacities (NTCs), there is a Link component which does controllable
power flow like a transport model (and can also represent a
point-to-point HVDC link).



Optimising total annual system costs
------------------------------------

To minimise long-run annual system costs for meeting an inelastic electrical
load, capital costs for transmission and generation should be set to
the annualised investment costs in e.g. EUR/MW/a, marginal costs for
dispatch to e.g. EUR/MWh and the weightings (now with units hours per
annum, h/a) are chosen such that


.. math::
   \sum_t w_t = 8760

In this case the objective function gives total system cost in EUR/a
to meet the total load.

Stochastic optimisation
-----------------------

For the very simplest stochastic optimisation you can use the
weightings ``w_t`` as probabilities for the snapshots, which can
represent different load/weather conditions. More sophisticated
functionality is planned.



Variables and notation summary
------------------------------

:math:`n \in N = \{0,\dots |N|-1\}` label the buses

:math:`t \in T = \{0,\dots |T|-1\}` label the snapshots

:math:`l \in L = \{0,\dots |L|-1\}` label the branches

:math:`s \in S = \{0,\dots |S|-1\}` label the different generator/storage types at each bus

:math:`w_t` weighting of time :math:`t` in the objective function

:math:`g_{n,s,t}` dispatch of generator :math:`s` at bus :math:`n` at time :math:`t`

:math:`\bar{g}_{n,s}` nominal power of generator :math:`s` at bus :math:`n`

:math:`\bar{g}_{n,s,t}` availability of  generator :math:`s` at bus :math:`n` at time :math:`t` per unit of nominal power

:math:`u_{n,s,t}` binary status variable for generator with unit commitment

:math:`suc_{n,s,t}` start-up cost if generator with unit commitment is started at time :math:`t`

:math:`sdc_{n,s,t}` shut-down cost if generator with unit commitment is shut down at time :math:`t`

:math:`c_{n,s}` capital cost of extending generator nominal power by one MW

:math:`o_{n,s}` marginal cost of dispatch generator for one MWh

:math:`f_{l,t}` flow of power in branch :math:`l` at time :math:`t`

:math:`F_{l}` capacity of branch :math:`l`

:math:`\eta_{n,s}` efficiency of generator :math:`s` at bus :math:`n`

:math:`\eta_{l}` efficiency of controllable link :math:`l`

:math:`e_s` CO2-equivalent-tonne-per-MWh of the fuel carrier :math:`s`


Further definitions are given below.

Objective function
------------------

See ``pypsa.opf.define_linear_objective(network,snapshots)``.

The objective function is composed of capital costs :math:`c` for each component and operation costs :math:`o` for generators

.. math::
   \sum_{n,s} c_{n,s} \bar{g}_{n,s} + \sum_{n,s} c_{n,s} \bar{h}_{n,s} + \sum_{l} c_{l} F_l \\
   + \sum_{t} w_t \left[\sum_{n,s} o_{n,s,t} g_{n,s,t} + \sum_{n,s} o_{n,s,t} h_{n,s,t} \right]
   + \sum_{t} \left[suc_{n,s,t} + sdc_{n,s,t} \right]


Additional variables which do not appear in the objective function are
the storage uptake variable, the state of charge and the voltage angle
for each bus.



Generator constraints
---------------------

These are defined in ``pypsa.opf.define_generator_variables_constraints(network,snapshots)``.

Generator nominal power and generator dispatch for each snapshot may be optimised.


Each generator has a dispatch variable :math:`g_{n,s,t}` where
:math:`n` labels the bus, :math:`s` labels the particular generator at
the bus (e.g. it can represent wind/gas/coal generators at the same
bus in an aggregated network) and :math:`t` labels the time.

It obeys the constraints:

.. math::
   \tilde{g}_{n,s,t}*\bar{g}_{n,s} \leq g_{n,s,t} \leq  \bar{g}_{n,s,t}*\bar{g}_{n,s}

where :math:`\bar{g}_{n,s}` is the nominal power (``generator.p_nom``)
and :math:`\tilde{g}_{n,s,t}` and :math:`\bar{g}_{n,s,t}` are
time-dependent restrictions on the dispatch (per unit of nominal
power) due to e.g. wind availability or power plant de-rating.

For generators with time-varying ``p_max_pu`` in ``network.generators_t`` the per unit
availability :math:`\bar{g}_{n,s,t}` is a time series.


For generators with static ``p_max_pu`` in ``network.generators`` the per unit
availability is a constant.


If the generator's nominal power :math:`\bar{g}_{n,s}` is also the
subject of optimisation (``generator.p_nom_extendable == True``) then
limits ``generator.p_nom_min`` and ``generator.p_nom_max`` on the
installable nominal power may also be introduced, e.g.



.. math::
   \tilde{g}_{n,s} \leq    \bar{g}_{n,s} \leq  \hat{g}_{n,s}





.. _unit-commitment:

Generator unit commitment constraints
-------------------------------------

These are defined in ``pypsa.opf.define_generator_variables_constraints(network,snapshots)``.

The implementation follows Chapter 4.3 of `Convex Optimization of Power Systems <http://www.cambridge.org/de/academic/subjects/engineering/control-systems-and-optimization/convex-optimization-power-systems>`_ by
Joshua Adam Taylor (CUP, 2015).


Unit commitment can be turned on for any generator by setting ``committable`` to be ``True``. This introduces a
times series of new binary status variables :math:`u_{n,s,t} \in \{0,1\}`,
which indicates whether the generator is running (1) or not (0) in
period :math:`t`. The restrictions on generator output now become:

.. math::
   u_{n,s,t}*\tilde{g}_{n,s,t}*\bar{g}_{n,s} \leq g_{n,s,t} \leq   u_{n,s,t}*\bar{g}_{n,s,t}*\bar{g}_{n,s} \hspace{.5cm} \forall\, n,s,t

so that if :math:`u_{n,s,t} = 0` then also :math:`g_{n,s,t} = 0`.

If :math:`T_{\textrm{min\_up}}` is the minimum up time then we have

.. math::
   \sum_{t'=t}^{t+T_\textrm{min\_up}} u_{n,s,t'}\geq T_\textrm{min\_up} (u_{n,s,t} - u_{n,s,t-1})   \hspace{.5cm} \forall\, n,s,t

(i.e. if the generator has just started up (:math:`u_{n,s,t} - u_{n,s,t-1} = 1`) then it has to run for at least :math:`T_{\textrm{min\_up}}` periods). Similarly for a minimum down time of :math:`T_{\textrm{min\_down}}`

.. math::
   \sum_{t'=t}^{t+T_\textrm{min\_down}} (1-u_{n,s,t'})\geq T_\textrm{min\_down} (u_{n,s,t-1} - u_{n,s,t})   \hspace{.5cm} \forall\, n,s,t


For non-zero start up costs :math:`suc_{n,s}` a new variable :math:`suc_{n,s,t} \geq 0` is introduced for each time period :math:`t` and added to the objective function.  The variable satisfies

.. math::
   suc_{n,s,t} \geq suc_{n,s} (u_{n,s,t} - u_{n,s,t-1})   \hspace{.5cm} \forall\, n,s,t

so that it is only non-zero if :math:`u_{n,s,t} - u_{n,s,t-1} = 1`, i.e. the generator has just started, in which case the inequality is saturated :math:`suc_{n,s,t} = suc_{n,s}`. Similarly for the shut down costs :math:`sdc_{n,s,t} \geq 0` we have

.. math::
   sdc_{n,s,t} \geq sdc_{n,s} (u_{n,s,t-1} - u_{n,s,t})   \hspace{.5cm} \forall\, n,s,t




.. _ramping:

Generator ramping constraints
-----------------------------

These are defined in ``pypsa.opf.define_generator_variables_constraints(network,snapshots)``.

The implementation follows Chapter 4.3 of `Convex Optimization of Power Systems <http://www.cambridge.org/de/academic/subjects/engineering/control-systems-and-optimization/convex-optimization-power-systems>`_ by
Joshua Adam Taylor (CUP, 2015).

Ramp rate limits can be defined for increasing power output
:math:`ru_{n,s}` and decreasing power output :math:`rd_{n,s}`. By
default these are null and ignored. They should be given per unit of
the generator nominal power. The generator dispatch then obeys

.. math::
   -rd_{n,s} * \bar{g}_{n,s} \leq (g_{n,s,t} - g_{n,s,t-1}) \leq ru_{n,s} * \bar{g}_{n,s}

for :math:`t \in \{1,\dots |T|-1\}`.

For generators with unit commitment you can also specify ramp limits
at start-up :math:`rusu_{n,s}` and shut-down :math:`rdsd_{n,s}`

.. math::
  \left[ -rd_{n,s}*u_{n,s,t} -rdsd_{n,s}(u_{n,s,t-1} - u_{n,s,t})\right] \bar{g}_{n,s} \leq (g_{n,s,t} - g_{n,s,t-1}) \leq \left[ru_{n,s}*u_{n,s,t-1} +   rusu_{n,s} (u_{n,s,t} - u_{n,s,t-1})\right]\bar{g}_{n,s}



Storage Unit constraints
------------------------

These are defined in ``pypsa.opf.define_storage_variables_constraints(network,snapshots)``.


Storage nominal power and dispatch for each snapshot may be optimised.

With a storage unit the maximum state of charge may not be independently optimised from the maximum power output (they're linked by the maximum hours variable) and the maximum power output is linked to the maximum power input. To optimise these capacities independently, build a storage unit out of the more fundamental ``Store`` and ``Link`` components.

The storage nominal power is given by :math:`\bar{h}_{n,s}`.

In contrast to the generator, which has one time-dependent variable, each storage unit has three:

The storage dispatch :math:`h_{n,s,t}` (when it depletes the state of charge):

.. math::
   0 \leq h_{n,s,t} \leq \bar{h}_{n,s}

The storage uptake :math:`f_{n,s,t}` (when it increases the state of charge):

.. math::
   0 \leq f_{n,s,t} \leq  \bar{h}_{n,s}

and the state of charge itself:

.. math::
   0\leq soc_{n,s,t} \leq r_{n,s} \bar{h}_{n,s}

where :math:`r_{n,s}` is the number of hours at nominal power that fill the state of charge.

The variables are related by

.. math::
   soc_{n,s,t} = \eta_{\textrm{stand};n,s}^{w_t} soc_{n,s,t-1} + \eta_{\textrm{store};n,s} w_t f_{n,s,t} -  \eta^{-1}_{\textrm{dispatch};n,s} w_t h_{n,s,t} + w_t\textrm{inflow}_{n,s,t} - w_t\textrm{spillage}_{n,s,t}

:math:`\eta_{\textrm{stand};n,s}` is the standing losses dues to
e.g. thermal losses for thermal
storage. :math:`\eta_{\textrm{store};n,s}` and
:math:`\eta_{\textrm{dispatch};n,s}` are the efficiency losses for
power going into and out of the storage unit.



There are two options for specifying the initial state of charge :math:`soc_{n,s,t=-1}`: you can set
``storage_unit.cyclic_state_of_charge = False`` (the default) and the value of
``storage_unit.state_of_charge_initial`` in MWh; or you can set
``storage_unit.cyclic_state_of_charge = True`` and then
the optimisation assumes :math:`soc_{n,s,t=-1} = soc_{n,s,t=|T|-1}`.



If in the time series ``storage_unit_t.state_of_charge_set`` there are
values which are not NaNs, then it will be assumed that these are
fixed state of charges desired for that time :math:`t` and these will
be added as extra constraints. (A possible usage case would be a
storage unit where the state of charge must empty every day.)


Store constraints
------------------------

These are defined in ``pypsa.opf.define_store_variables_constraints(network,snapshots)``.

Store nominal energy and dispatch for each snapshot may be optimised.

The store nominal energy is given by :math:`\bar{e}_{n,s}`.

The store has two time-dependent variables:

The store dispatch :math:`h_{n,s,t}`:

.. math::
   -\infty \leq h_{n,s,t} \leq +\infty

and the energy:

.. math::
   \tilde{e}_{n,s} \leq e_{n,s,t} \leq \bar{e}_{n,s}


The variables are related by

.. math::
   e_{n,s,t} = \eta_{\textrm{stand};n,s}^{w_t} e_{n,s,t-1} - w_t h_{n,s,t}

:math:`\eta_{\textrm{stand};n,s}` is the standing losses dues to
e.g. thermal losses for thermal
storage.

There are two options for specifying the initial energy
:math:`e_{n,s,t=-1}`: you can set
``store.e_cyclic = False`` (the default) and the
value of ``store.e_initial`` in MWh; or you can
set ``store.e_cyclic = True`` and then the
optimisation assumes :math:`e_{n,s,t=-1} = e_{n,s,t=|T|-1}`.



Passive branch flows: lines and transformers
--------------------------------------------

See ``pypsa.opf.define_passive_branch_flows(network,snapshots)`` and
``pypsa.opf.define_passive_branch_constraints(network,snapshots)`` and ``pypsa.opf.define_branch_extension_variables(network,snapshots)``.





For lines and transformers, whose power flows according to impedances,
the power flow :math:`f_{l,t}` in AC networks is given by the difference in voltage
angles :math:`\theta_{n,t}` at bus0 and :math:`\theta_{m,t}` at bus1 divided by the series reactance :math:`x_l`


.. math::
   f_{l,t} = \frac{\theta_{n,t} - \theta_{m,t}}{x_l}


(For DC networks, replace the voltage angles by the difference in voltage magnitude :math:`\delta V_{n,t}` and the series reactance by the series resistance :math:`r_l`.)


This flow is the limited by the capacity :math:``F_l`` of the line


.. math::
   |f_{l,t}| \leq F_l

Note that if :math:`F_l` is also subject to optimisation
(``branch.s_nom_extendable == True``), then the impedance :math:`x` of
the line is NOT automatically changed with the capacity (to represent
e.g. parallel lines being added).

There are two choices here:

Iterate the LOPF again with the updated impedances (see e.g. `<http://www.sciencedirect.com/science/article/pii/S0360544214000322#>`_).

João Gorenstein Dedecca has also implemented a MILP version of the
transmission expansion, see
`<https://github.com/jdedecca/MILP_PyPSA>`_, which properly takes
account of the impedance with a disjunctive relaxation. This will be
pulled into the main PyPSA code base soon.


.. _formulations:

Passive branch flow formulations
--------------------------------

PyPSA implements four formulations of the linear power flow equations
that are mathematically equivalent, but may have different
solving times. These different formulations are described and
benchmarked in the arXiv preprint paper `Linear Optimal Power Flow Using
Cycle Flows <https://arxiv.org/abs/1704.01881>`_.

You can choose the formulation by passing ``network.lopf`` the
argument ``formulation``, which must be in
``["angles","cycles","kirchhoff","ptdf"]``. ``angles`` is the standard
formulations based on voltage angles described above, used for the
linear power flow and found in textbooks. ``ptdf`` uses the Power
Transfer Distribution Factor (PTDF) formulation, found for example in
`<http://www.sciencedirect.com/science/article/pii/S0360544214000322#>`_. ``kirchhoff``
and ``cycles`` are two new formulations based on a graph-theoretic
decomposition of the network flows into a spanning tree and closed
cycles.

Based on the benchmarking in `Linear Optimal Power Flow Using Cycle
Flows <https://arxiv.org/abs/1704.01881>`_ for standard networks,
``kirchhoff`` almost always solves fastest, averaging 3 times faster
than the ``angles`` formulation and up to 20 times faster in specific
cases. The speedup is higher for larger networks with dispatchable
generators at most nodes.


.. _opf-links:

Controllable branch flows: links
---------------------------------

See ``pypsa.opf.define_controllable_branch_flows(network,snapshots)``
and ``pypsa.opf.define_branch_extension_variables(network,snapshots)``.


For links, whose power flow is controllable, there is simply an
optimisation variable for each component which satisfies

.. math::
   |f_{l,t}| \leq F_l

If the link flow is positive :math:`f_{l,t} > 0` then it withdraws
:math:`f_{l,t}` from ``bus0`` and feeds in :math:`\eta_l f_{l,t}` to
``bus1``, where :math:`\eta_l` is the link efficiency.

If additional output buses ``busi`` for :math:`i=2,3,\dots` are
defined (i.e. ``bus2``, ``bus3``, etc) and their associated
efficiencies ``efficiencyi``, i.e. :math:`\eta_{i,l}`, then at
``busi`` the feed-in is :math:`\eta_{i,l} f_{l,t}`. See also
:ref:`components-links-multiple-outputs`.


.. _nodal-power-balance:

Nodal power balances
--------------------

See ``pypsa.opf.define_nodal_balances(network,snapshots)``.

This is the most important equation, which guarantees that the power
balances at each bus :math:`n` for each time :math:`t`.

.. math::
   \sum_{s} g_{n,s,t} + \sum_{s} h_{n,s,t} - \sum_{s} f_{n,s,t} - \sum_{l} K_{nl} f_{l,t} = \sum_{s} d_{n,s,t} \hspace{.4cm} \leftrightarrow  \hspace{.4cm} w_t\lambda_{n,t}

Where :math:`d_{n,s,t}` is the exogenous load at each node (``load.p_set``) and the incidence matrix :math:`K_{nl}` for the graph takes values in :math:`\{-1,0,1\}` depending on whether the branch :math:`l` ends or starts at the bus. :math:`\lambda_{n,t}` is the shadow price of the constraint, i.e. the locational marginal price, stored in ``network.buses_t.marginal_price``.


The bus's role is to enforce energy conservation for all elements
feeding in and out of it (i.e. like Kirchhoff's Current Law).

.. image:: img/buses.png



.. _global-constraints-opf:

Global constraints
------------------

See ``pypsa.opf.define_global_constraints(network,snapshots)``.

Global constraints apply to more than one component.

Currently only "primary energy" constraints are defined. They depend
on the power plant efficiency and carrier-specific attributes such as
specific CO2 emissions.


Suppose there is a global constraint defined for CO2 emissions with
sense ``<=`` and constant ``\textrm{CAP}_{CO2}``. Emissions can come
from generators whose energy carriers have CO2 emissions and from
stores and storage units whose storage medium releases or absorbs CO2
when it is converted. Only stores and storage units with non-cyclic
state of charge that is different at the start and end of the
simulation can contribute.

If the specific emissions of energy carrier :math:`s` is :math:`e_s`
(``carrier.co2_emissions``) CO2-equivalent-tonne-per-MWh and the
generator with carrier :math:`s` at node :math:`n` has efficiency
:math:`\eta_{n,s}` then the CO2 constraint is

.. math::
   \sum_{n,s,t} \frac{1}{\eta_{n,s}} w_t\cdot g_{n,s,t}\cdot e_{n,s} + \sum_{n,s}\left(e_{n,s,t=-1} - e_{n,s,t=|T|-1}\right) \cdot e_{n,s} \leq  \textrm{CAP}_{CO2}  \hspace{.4cm} \leftrightarrow  \hspace{.4cm} \mu

The first sum is over generators; the second sum is over stores and
storage units. :math:`\mu` is the shadow price of the constraint,
i.e. the CO2 price in this case. :math:`\mu` is an output of the
optimisation stored in ``network.global_constraints.mu``.


Custom constraints and other functionality
------------------------------------------

PyPSA uses the Python optimisation language `pyomo
<http://www.pyomo.org/>`_ to construct the OPF problem. You can easily
extend the optimisation problem constructed by PyPSA using the usual
pyomo syntax. To do this, pass the function ``network.lopf`` a
function ``extra_functionality`` as an argument.  This function must
take two arguments ``extra_functionality(network,snapshots)`` and is
called after the model building is complete, but before it is sent to
the solver. It allows the user to add, change or remove constraints
and alter the objective function.

The `CHP example
<https://pypsa.org/examples/power-to-gas-boiler-chp.html>`_ and the
`example that replaces generators and storage units with fundamental links
and stores
<https://pypsa.org/examples/replace-generator-storage-units-with-store.html>`_
both pass an ``extra_functionality`` argument to the LOPF to add
functionality.

The function ``extra_postprocessing`` is called after the model has
solved and the results are extracted.  This function must take three
arguments `extra_postprocessing(network,snapshots,duals)`. It allows
the user to extract further information about the solution, such as
additional shadow prices for constraints.


Inputs
------

For the linear optimal power flow, the following data for each component
are used. For almost all values, defaults are assumed if not
explicitly set. For the defaults and units, see :doc:`components`.

network{snapshot_weightings}

bus.{v_nom, carrier}

load.{p_set}

generator.{p_nom, p_nom_extendable, p_nom_min, p_nom_max, p_min_pu, p_max_pu, marginal_cost, capital_cost, efficiency, carrier}

storage_unit.{p_nom, p_nom_extendable, p_nom_min, p_nom_max, p_min_pu, p_max_pu, marginal_cost, capital_cost, efficiency*, standing_loss, inflow, state_of_charge_set, max_hours, state_of_charge_initial, cyclic_state_of_charge}

store.{e_nom, e_nom_extendable, e_nom_min, e_nom_max, e_min_pu, e_max_pu, e_cyclic, e_initial, capital_cost, marginal_cost, standing_loss}

line.{x, s_nom, s_nom_extendable, s_nom_min, s_nom_max, capital_cost}

transformer.{x, s_nom, s_nom_extendable, s_nom_min, s_nom_max, capital_cost}

link.{p_min_pu, p_max_pu, p_nom, p_nom_extendable, p_nom_min, p_nom_max, capital_cost}

carrier.{carrier_attribute}

global_constraint.{type, carrier_attribute, sense, constant}

Note that for lines and transformers you MUST make sure that
:math:`x` is non-zero, otherwise the bus admittance matrix will be singular.

Outputs
-------

bus.{v_mag_pu, v_ang, p, marginal_price}

load.{p}

generator.{p, p_nom_opt}

storage_unit.{p, p_nom_opt, state_of_charge, spill}

store.{p, e_nom_opt, e}

line.{p0, p1, s_nom_opt, mu_lower, mu_upper}

transformer.{p0, p1, s_nom_opt, mu_lower, mu_upper}

link.{p0, p1, p_nom_opt, mu_lower, mu_upper}

global_constraint.{mu}
