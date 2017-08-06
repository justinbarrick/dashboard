.PHONY: build
build:
	docker-compose build

.PHONY: test
test:
	docker-compose run dashboard-test

.PHONY: run
run:
	docker-compose run dashboard

.PHONY: browser
browser:
	chromium http://$(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(shell docker-compose ps -q dashboard |tail -n1)):8080/
