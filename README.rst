\army\
==========

Army is a plugin centric package manager dedicated to write firmware for 
the arm microcontroler world.  

Army in itself is only a package manager but once enhanced with toolchain
plugins it quicly becomes a useful tool to manage your dependencies and 
firmware versions.  

Army quick tour:

-   Command line tool
-   Package manager with semantic versioning  
-   Plugin centric 


Installing
----------

Install and update using `pip`_:

.. code-block:: text

    $ pip install -U army

.. _pip: https://pip.pypa.io/en/stable/quickstart/


Links
-----

-   Documentation: https://army.readthedocs.io/en/latest/
-   Releases: https://github.com/turdusmerula/army/releases
-   Code: https://github.com/turdusmerula/army
-   Issue tracker: https://github.com/turdusmerula/army/issues
-   Tests: https://travis-ci.com/github/turdusmerula/army

TODO
----

- template version -> for application and documentation
- write proper unit tests
- improve argparse annotations for better error handling
- improve substitution not found warning on dict_file
