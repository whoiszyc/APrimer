#######
 Design
#######


Python 2 and Python 3 compatible
================================

PyPSA is written and tested to be compatible with both Python 2.7 and
Python 3.5.



Network object is the overall container
=======================================

The ``pypsa.Network`` is an overall container for all network
components; components cannot exist without a network.

It is also the object on which calculations, such as power flow and
optimal power flow, are performed.


Buses are the fundamental nodes
===============================

The bus is the fundamental node to which all loads, generators,
storage units, lines, transformers and links attach.

You can have as many components attached to a bus as you want.

The bus's role is to enforce energy conservation for all elements
feeding in and out of it (i.e. like Kirchhoff's Current Law).


.. image:: img/buses.png


Energy flow in the model
========================

Energy enters the model in generators, storage units or stores with
higher energy before than after the simulation, and any components
with efficiency greater than 1 (e.g. heat pumps).

Energy leaves the model in loads, storage units or stores with higher
energy after than before the simulation, and in lines, links or
storage units with efficiency less than 1.



Data is stored in pandas DataFrames
===================================

To enable efficient calculations on the different dimensions of the
data, data is stored in memory using pandas DataFrames.

Other power system toolboxes use databases for data storage; given
modern RAM availability and speed considerations, pandas DataFrames
were felt to be preferable and simpler.


To see which data is stored for each component, see :doc:`components`.


Static component data
=====================

For each component type (line, transformer, generator, etc.), which
must be uniquely named for each network, its basic static data is
stored in a pandas DataFrame, which is an attribute of the network
object, with names that follow the component names:

* network.buses
* network.generators
* network.loads
* network.lines
* network.transformers

These are all pandas DataFrames, indexed by the unique name of the
component.

The columns contain data such as impedance, capacity and the buses to
which components are attached. All attributes for each component type
are listed with their properties (defaults, etc.) in :doc:`components`
and are accessible from the network object in
e.g. ``network.components["Bus"]["attrs"]``.


Network components cannot exist without a network to hold them.



.. _time-varying:

Time-varying data
=================

Some quantities, such as generator ``p_set`` (generator active power
set point), generator ``p`` (generator calculated active power), line
``p0`` (line active power at ``bus0``) and line ``p1`` (line active
power at ``bus1``) may vary over time, so PyPSA offers the possibility
to store different values of these attributes for the different
snapshots in ``network.snapshots`` in the following attributes of the
network object:

* network.buses_t
* network.generators_t
* network.loads_t
* network.lines_t
* network.transformers_t

These are all dictionaries of pandas DataFrames, so that for example
``network.generators_t["p_set"]`` is a DataFrame with columns
corresponding to generator names and index corresponding to
``network.snapshots``. You can also access the dictionary like an
attribute ``network.generators_t.p_set``.

Time-varying data are defined as ``series`` in the listings in  :doc:`components`.


For **input data** such as ``p_set`` of a generator you can store the
value statically in ``network.generators`` if the value does not
change over ``network.snapshots`` **or** you can define it to be
time-varying by adding a column to ``network.generators_t.p_set``. If
the name of the generator is in the columns of
``network.generators_t.p_set``, then the static value in
``network.generators`` will be ignored. Some example definitions of
input data:


.. code:: python

    #four snapshots are defined by integers
    network.set_snapshots(range(4))

    network.add("Bus", "my bus")

    #add a generator whose output does not change over time
    network.add("Generator", "Coal", bus="my bus", p_set=100)

    #add a generator whose output does change over time
    network.add("Generator", "Wind", bus="my bus", p_set=[10,50,20,30])

In this case only the generator "Wind" will appear in the columns of
``network.generators_t.p_set``.

For **output data**, all time-varying data is stored in the
``network.components_t`` dictionaries, but it is only defined once a
simulation has been run.



No GUI: Use Jupyter notebooks
=============================

PyPSA has no Graphical User Interface (GUI). However it has features
for plotting time series and networks (e.g. ``network.plot()``), which
works especially well in combination with `Jupyter notebooks
<http://jupyter.org/>`_.

Internal use of per unit
===========================

Per unit values of voltage and impedance are used internally for
network calculations. It is assumed internally that the base power is
1 MVA. The base voltage depends on the component.

See also :ref:`unit-conventions`.


Set points are stored separately from actual dispatch points
============================================================

Dispatchable generators have a p_set series which is separate from the
calculated active power series p, since the operators's intention may
be different from what is calculated (e.g. when using distributed
slack for the active power).


Pyomo for the optimisation framework
====================================

To enable portability between solvers, the OPF is formulated using the
Python optimisation modelling package `pyomo <http://www.pyomo.org/>`_
(which can be thought of as a Python version of `GAMS
<http://www.gams.de/>`_).

Pyomo also has useful features such as index sets, etc.
