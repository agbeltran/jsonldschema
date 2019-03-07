.. jsonldschema documentation master file, created by
   sphinx-quickstart on Mon Oct 29 15:20:58 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to jsonldschema's documentation!
========================================

The JSONLDschema python package offers functionality to support the creation and use of machine-actionable and FAIR (Findable, Accessible, Interoperable and Reusable) metadata models expressed as `JSON-schemas <https://json-schema.org/>`_ for `JSON-LD <http://json-ld.org/>`_ data.

The approach relies on representing the metadata models as JSON-schemas with additional JSON-LD context files to provide semantic annotations to the model.

This python package can be used in combination with some visualisation tools:

* the JSONschema-documenter: given a network of JSON-schemas (formed by a main schema that references other schemas), it visualises them on the web
   * the source code available on GitHub: https://github.com/FAIRsharing/JSONschema-documenter
   * the tool is hosted on GitHub and can be seen here: https://fairsharing.github.io/JSONschema-documenter/
* the JSONschema-compare-and-view tool:
   * the source code is available on GitHub: https://github.com/FAIRsharing/JSONschema-compare-and-view
   * the tool is hosted on GitHub and can be seen here: https://fairsharing.github.io/JSONschema-compare-and-view/

We have used this approach in several metadata models, such as the Data Tag Suite (DATS) and a

.. toctree::
      :titlesonly:
      :numbered:

      semDiff/semDiffIndex
      cedar/cedarIndex
      utils/utilsIndex
      validation/validationIndex
      API/apiIndex


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
