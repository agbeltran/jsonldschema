Module for validation methods, including validation of JSON schemas.

In order to extract a compliant JSON from the FlowRepository API XMLs you need to provide:
- your FlowRepository ID in tests/test_config.json
- create a JSON containing the mapping between the FlowRepository fields and the instance fields
. In order to do that, you can:
    - provide fields as string (the default OptionalS bender object will be used)
    - provide fields as objects containing:
        - the field value ("value")
        - the bender object to use ("benderOption") between default (OptionalS), raiseErrors (S)
        , simple (K) and inject (F).
For more information on which bender object to use please refer to https://github.com/Onyo/jsonbender