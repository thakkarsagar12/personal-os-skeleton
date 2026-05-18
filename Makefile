.DEFAULT_GOAL := help
.PHONY: help init doctor scan test
help:    ; @printf 'Targets:\n  help    show this list (default)\n  init    run ./setup.sh\n  doctor  run ./scripts/doctor.sh\n  scan    run privacy scan (./scripts/make-shareable.sh)\n  test    run test suite (bash tests/run.sh)\n'
init:    ; ./setup.sh
doctor:  ; ./scripts/doctor.sh
scan:    ; ./scripts/make-shareable.sh
test:    ; bash tests/run.sh
