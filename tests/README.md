# Gating testplans for compiler-rt

The tests for compiler-rt are in a separate repo: https://src.fedoraproject.org/tests/compiler-rt
This directory should contain only fmf plans (such as build-gating.fmf) which import
the tests from the tests repo. This can be done using the "url" parameter of the
plan's "discover" step. Reference: https://tmt.readthedocs.io/en/stable/spec/plans.html#fmf
