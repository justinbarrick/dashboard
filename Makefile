.PHONY: build
build:
	docker-compose -f docker/docker-compose.yml build

.PHONY: test
test:
	docker-compose -f docker/docker-compose.yml run dashboard-test

.PHONY: run
run:
	docker-compose -f docker/docker-compose.yml run --service-ports dashboard

.PHONY: browser
browser:
	chromium http://$(shell docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(shell docker-compose -f docker/docker-compose.yml ps -q dashboard |tail -n1)):8080/

.PHONY: mac-browser
mac-browser:
	open -a firefox http://127.0.0.1:$(shell docker inspect -f '{{(index (index .NetworkSettings.Ports "8080/tcp") 0).HostPort}}' $(shell docker-compose -f docker/docker-compose.yml ps -q dashboard |tail -n1))/
