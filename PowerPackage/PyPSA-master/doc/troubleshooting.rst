################
Troubleshooting
################

Library dependency issues
=========================

If you are experiencing problems with PyPSA or with the importing of
the libraries on which PyPSA depends, please first check that you are
working with the latest versions of all packages.

See :ref:`upgrading-packages` and :ref:`upgrading-pypsa`.


Consistency check on network
============================

Running ``network.consistency_check()`` will examine the network
components to make sure that all components are connected to existing
buses and that no impedances are singular.



Problems with power flow convergence
====================================

If your ``network.pf()`` is not converging there are two possible reasons:

* The problem you have defined is not solvable (e.g. because in
  reality you would have a voltage collapse)
* The problem is solvable, but there are numerical instabilities in
  the solving algorithm (e.g. Newton-Raphson is known not to
  converge even for solvable problems; or the flat solution PyPSA
  uses as an initial guess is too far from the correction solution
  because of transformer phase-shifts)

There are some steps you can take to distinguish these two cases:

* Check the units you have used to define the problem are correct; see
  :doc:`conventions`. If your units are out by a factor 1000
  (e.g. using kW instead of MW) don't be surprised if your problem is
  no longer solvable.
* Check with a linear power flow ``network.lpf()`` that all voltage
  angles differences across branches are less than 40 degrees. You can do this with the following code:

.. code:: python

   import pandas as pd, numpy as np

   now = network.snapshots[0]

   angle_diff = pd.Series(network.buses_t.v_ang.loc[now,network.lines.bus0].values -    network.buses_t.v_ang.loc[now,network.lines.bus1].values,index=network.lines.index)

   (angle_diff*180/np.pi).describe()

* You can seed the non-linear power flow initial guess with the
  voltage angles from the linear power flow. This is advisable if you
  have transformers with phase shifts in the network, which lead to
  solutions far away from the flat initial guess of all voltage angles
  being zero. To seed the problem activate the ``use_seed`` switch:

.. code:: python

   network.lpf()
   network.pf(use_seed=True)


* Reduce all power values ``p_set`` and ``q_set`` of generators and
  loads to a fraction, e.g. 10%, solve the load flow and use it as a
  seed for the power at 20%, iteratively up to 100%.


Pitfalls/Gotchas
================

Some attributes are generated dynamically and are therefore only
copies. If you change data in them, this will NOT update the original
data. They are all defined as functions to make this clear.

For example:

* ``network.branches()`` returns a DataFrame which is a concatenation
  of ``network.lines`` and ``network.transformers``
* ``sub_network.generators()`` returns a DataFrame consisting of
  generators in ``sub_network``


Reporting bugs/issues
=====================

Please do not contact the developers directly.

Please report questions to the `mailing list
<https://groups.google.com/group/pypsa>`_.

If you're relatively certain you've found a bug, raise it as an issue
on the `PyPSA Github Issues page
<https://github.com/PyPSA/PyPSA/issues>`_.
