.PHONY: build
build:
	docker-compose -f docker/docker-compose.yml build

.PHONY: test
test:
	docker-compose -f docker/docker-compose.yml run dashboard-test

.PHONY: run
run:
	docker-compose -f docker/docker-compose.yml run dashboard

.PHONY: browser
browser:
	chromium http://$(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(shell docker-compose -f docker/docker-compose.yml ps -q dashboard |tail -n1)):8080/
