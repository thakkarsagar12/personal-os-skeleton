.PHONY: init doctor scan test
init:    ; ./setup.sh
doctor:  ; ./scripts/doctor.sh
scan:    ; ./scripts/make-shareable.sh
test:    ; bash tests/run.sh
